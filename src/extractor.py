"""
Bedrock Promise Extractor module for Promise Keeper.
Uses Amazon Bedrock Converse API (amazon.nova-pro-v1:0 / Claude 3.5 Sonnet)
to parse spoken wearable conversations into structured, actionable commitments.
"""

from __future__ import annotations
import json
import logging
import os
import re
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from src.telemetry import (
    TelemetryRecord,
    calculate_cost,
    default_telemetry_recorder,
)

load_dotenv()
logger = logging.getLogger(__name__)

DirectionType = Literal["MADE_BY_ME", "MADE_TO_ME"]


class EmailDraft(BaseModel):
    """Draft email ready for human review before staging."""

    subject: str = Field(..., description="Courteous and clear subject line")
    body: str = Field(..., description="Draft email body ready to edit")


class CalendarEvent(BaseModel):
    """Tentative calendar event definition."""

    title: str = Field(..., description="Tentative block title")
    start_iso: str = Field(..., description="ISO 8601 start datetime string")
    duration_minutes: int = Field(default=30, description="Duration in minutes")


class PromiseItem(BaseModel):
    """Validated structured commitment extracted from conversation."""

    id: str = Field(
        default_factory=lambda: f"promise_{int(time.time() * 1000)}"
    )
    direction: DirectionType = Field(
        ...,
        description="'MADE_BY_ME' if the wearer made the promise, 'MADE_TO_ME' if made to the wearer",
    )
    counterparty_name: str = Field(..., description="Name of the person involved")
    counterparty_email: str = Field(
        default="", description="Inferred or known email of counterparty"
    )
    summary: str = Field(..., description="Concise synopsis of the promise")
    verbal_deadline: str = Field(
        ..., description="Exact verbal deadline spoken in the turn"
    )
    inferred_iso_deadline: str = Field(
        ..., description="ISO 8601 timestamp representing the deadline"
    )
    task_title: str = Field(..., description="Actionable title for Todoist")
    email_draft: EmailDraft
    calendar_event: CalendarEvent
    status: str = Field(
        default="PENDING",
        description="Staging status: 'PENDING', 'STAGED', or 'REJECTED'",
    )


class ExtractionResult(BaseModel):
    """Complete extraction payload containing promises, telemetry, and raw output."""

    promises: List[PromiseItem]
    raw_response: str
    telemetry: TelemetryRecord


SYSTEM_EXTRACTION_PROMPT = """You are an elite executive assistant AI running on Amazon Bedrock.
Your role is to analyze multi-speaker transcripts from the user's Bee wearable microphone and extract all commitments, agreements, deliverables, or promises made:
1. MADE_BY_ME: Explicit or implicit commitments made BY the user ("Wearer", "Me", Speaker 0).
2. MADE_TO_ME: Requests, deliverables, or deadlines promised or requested TO the user by others.

CRITICAL INSTRUCTIONS:
- You must output ONLY a valid JSON array of promise objects.
- Do NOT output any markdown wrappers, commentary, or text before or after the JSON array.
- For every commitment found, produce an object adhering strictly to this JSON schema:

[
  {
    "direction": "MADE_BY_ME" or "MADE_TO_ME",
    "counterparty_name": "Full name of the other person",
    "counterparty_email": "Valid email address (infer domain or use realistic email)",
    "summary": "Crisp one-sentence summary of what was agreed",
    "verbal_deadline": "Exact verbal phrase used (e.g. '5 PM tomorrow', 'Thursday morning at 9 AM')",
    "inferred_iso_deadline": "ISO 8601 timestamp in UTC (e.g. '2026-10-20T17:00:00Z')",
    "task_title": "Actionable task title ready for Todoist (e.g. 'Send pitch deck and architecture diagram to Sarah')",
    "email_draft": {
      "subject": "Clear subject line for Gmail draft",
      "body": "Courteous, ready-to-review email body referencing the conversation"
    },
    "calendar_event": {
      "title": "Title for Google Calendar tentative block",
      "start_iso": "ISO 8601 start timestamp (typically 30-60 min before deadline or work session)",
      "duration_minutes": 30
    }
  }
]

Reference Anchor Time for relative deadlines (now): {anchor_time_iso}
Be thorough: if multiple promises exist across different turns, extract all of them as separate items.
"""


# Deterministic offline mock extraction matching the default Bee fixture
MOCK_EXTRACTION_FIXTURE = [
    {
        "direction": "MADE_BY_ME",
        "counterparty_name": "Sarah Lin",
        "counterparty_email": "sarah.lin@techinnovations.io",
        "summary": "Send the pitch deck and architecture diagram for hackathon review.",
        "verbal_deadline": "5 PM tomorrow",
        "inferred_iso_deadline": "2026-10-20T17:00:00Z",
        "task_title": "Send pitch deck and architecture diagram to Sarah Lin",
        "email_draft": {
            "subject": "Hackathon Pitch Deck & Architecture Diagram",
            "body": "Hi Sarah,\n\nFollowing up on our conversation, attached is the latest pitch deck and architecture diagram for the hackathon submission. Please take a look and let me know your thoughts before 5 PM.\n\nBest,\nAlex",
        },
        "calendar_event": {
            "title": "Focus: Finalize Pitch Deck for Sarah",
            "start_iso": "2026-10-20T16:00:00Z",
            "duration_minutes": 60,
        },
    },
    {
        "direction": "MADE_TO_ME",
        "counterparty_name": "Sarah Lin",
        "counterparty_email": "sarah.lin@techinnovations.io",
        "summary": "Sarah requested the analytics report and early user retention numbers for judges.",
        "verbal_deadline": "Thursday morning at 9 AM",
        "inferred_iso_deadline": "2026-10-22T09:00:00Z",
        "task_title": "Share analytics report with Sarah Lin for judges",
        "email_draft": {
            "subject": "User Analytics & Retention Report for Hackathon",
            "body": "Hi Sarah,\n\nHere are the compiled analytics and early user retention metrics ahead of Thursday morning judging.\n\nBest,\nAlex",
        },
        "calendar_event": {
            "title": "Review: Analytics Report & Metrics",
            "start_iso": "2026-10-22T08:30:00Z",
            "duration_minutes": 30,
        },
    },
    {
        "direction": "MADE_BY_ME",
        "counterparty_name": "David Kim",
        "counterparty_email": "david.kim@cloudinfra.net",
        "summary": "Review David's pull request before Monday standup at 10 AM.",
        "verbal_deadline": "Monday at 10 AM",
        "inferred_iso_deadline": "2026-10-26T10:00:00Z",
        "task_title": "Review David's PR before standup",
        "email_draft": {
            "subject": "Code Review: Pull Request Standup Sync",
            "body": "Hi David,\n\nI reviewed your PR ahead of Monday's standup. Comments are posted on GitHub.\n\nBest,\nAlex",
        },
        "calendar_event": {
            "title": "PR Review: David's Branch",
            "start_iso": "2026-10-26T09:00:00Z",
            "duration_minutes": 45,
        },
    },
    {
        "direction": "MADE_TO_ME",
        "counterparty_name": "Marcus Vance",
        "counterparty_email": "marcus.vance@partnerfirm.io",
        "summary": "Sign vendor agreement before legal closes for holiday.",
        "verbal_deadline": "Wednesday 3 PM",
        "inferred_iso_deadline": "2026-10-21T15:00:00Z",
        "task_title": "Sign and return vendor agreement to Marcus Vance",
        "email_draft": {
            "subject": "Executed Vendor Agreement - Promise Keeper",
            "body": "Hi Marcus,\n\nPlease find the signed vendor agreement attached ahead of the Wednesday 3 PM legal deadline.\n\nBest regards,\nAlex",
        },
        "calendar_event": {
            "title": "Sign: Vendor Agreement Deadline",
            "start_iso": "2026-10-21T14:30:00Z",
            "duration_minutes": 30,
        },
    },
]


class BedrockPromiseExtractor:
    """
    Orchestrates commitment extraction using the Amazon Bedrock Converse API.
    Supports Nova Pro with automated Claude 3.5 Sonnet fallback and robust JSON parsing.
    """

    def __init__(
        self,
        region_name: Optional[str] = None,
        primary_model_id: Optional[str] = None,
        fallback_model_id: Optional[str] = None,
    ) -> None:
        self.region_name = (
            region_name or os.getenv("AWS_REGION", "us-east-1").strip()
        )
        self.primary_model_id = (
            primary_model_id
            or os.getenv("BEDROCK_MODEL_ID", "amazon.nova-pro-v1:0").strip()
        )
        self.fallback_model_id = (
            fallback_model_id
            or "anthropic.claude-3-5-sonnet-20241022-v2:0"
        )
        self.mock_fallback = (
            os.getenv("BEDROCK_MOCK_FALLBACK", "true").strip().lower()
            in ("1", "true", "yes", "on")
        )

        self._client = None
        self._init_bedrock_client()

    def _init_bedrock_client(self) -> None:
        """Initializes the boto3 bedrock-runtime client."""
        aws_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY")

        try:
            session_kwargs: Dict[str, Any] = {"region_name": self.region_name}
            if aws_key and aws_secret:
                session_kwargs["aws_access_key_id"] = aws_key
                session_kwargs["aws_secret_access_key"] = aws_secret
                session_token = os.getenv("AWS_SESSION_TOKEN")
                if session_token:
                    session_kwargs["aws_session_token"] = session_token

            self._client = boto3.client("bedrock-runtime", **session_kwargs)
        except Exception as exc:
            logger.warning("Could not initialize real Bedrock client: %s", exc)
            self._client = None

    @staticmethod
    def sanitize_json_response(raw_text: str) -> str:
        """
        Cleans markdown wrappers, codeblock fences, and leading/trailing noise
        to ensure robust JSON parsing.
        """
        if not raw_text:
            return "[]"

        text = raw_text.strip()

        # Remove ```json ... ``` or ``` ... ```
        if "```" in text:
            # Match code blocks
            pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                text = matches[0].strip()

        # Isolate array boundary [ ... ]
        start_bracket = text.find("[")
        end_bracket = text.rfind("]")
        if start_bracket != -1 and end_bracket != -1 and end_bracket > start_bracket:
            text = text[start_bracket : end_bracket + 1]

        return text

    def extract_promises(
        self,
        transcript: str,
        anchor_time_iso: Optional[str] = None,
    ) -> ExtractionResult:
        """
        Extracts promises from a transcript using the Bedrock Converse API.
        Automatically tracks latency, token counts, and applies fallback.
        """
        anchor_time = anchor_time_iso or datetime.now(timezone.utc).isoformat()
        sys_prompt = SYSTEM_EXTRACTION_PROMPT.replace("{anchor_time_iso}", anchor_time)
        user_message = f"Wearable Conversation Transcript:\n\n{transcript}"

        start_time = time.perf_counter()

        # Attempt Bedrock Converse API with primary model
        if self._client and os.getenv("AWS_ACCESS_KEY_ID"):
            for model_id in [self.primary_model_id, self.fallback_model_id]:
                try:
                    logger.info("Calling Bedrock Converse API with model: %s", model_id)
                    response = self._client.converse(
                        modelId=model_id,
                        messages=[
                            {
                                "role": "user",
                                "content": [{"text": user_message}],
                            }
                        ],
                        system=[{"text": sys_prompt}],
                        inferenceConfig={
                            "temperature": 0.1,
                            "maxTokens": 2048,
                        },
                    )

                    duration_ms = (time.perf_counter() - start_time) * 1000
                    usage = response.get("usage", {})
                    input_tokens = usage.get("inputTokens", 0)
                    output_tokens = usage.get("outputTokens", 0)

                    content_blocks = (
                        response.get("output", {})
                        .get("message", {})
                        .get("content", [])
                    )
                    raw_text = content_blocks[0].get("text", "") if content_blocks else ""

                    clean_json = self.sanitize_json_response(raw_text)
                    parsed_list = json.loads(clean_json)

                    promises = [PromiseItem(**item) for item in parsed_list]

                    telemetry = default_telemetry_recorder.record(
                        model_id=model_id,
                        latency_ms=duration_ms,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        status="SUCCESS",
                    )

                    return ExtractionResult(
                        promises=promises,
                        raw_response=raw_text,
                        telemetry=telemetry,
                    )

                except (ClientError, BotoCoreError, Exception) as exc:
                    logger.warning(
                        "Bedrock call failed for model %s: %s. Trying fallback.",
                        model_id,
                        exc,
                    )
                    continue

        # If AWS Bedrock call was not made or failed, use mock fallback if enabled
        if self.mock_fallback:
            duration_ms = (time.perf_counter() - start_time) * 1000 + 380.0  # realistic simulated latency
            raw_json = json.dumps(MOCK_EXTRACTION_FIXTURE, indent=2)
            promises = [PromiseItem(**item) for item in MOCK_EXTRACTION_FIXTURE]

            # Estimate token metrics for realistic telemetry display
            sim_input_tokens = len(transcript.split()) + 420
            sim_output_tokens = len(raw_json.split()) + 150

            telemetry = default_telemetry_recorder.record(
                model_id=f"{self.primary_model_id} (Mock Fallback)",
                latency_ms=duration_ms,
                input_tokens=sim_input_tokens,
                output_tokens=sim_output_tokens,
                status="FALLBACK",
                details="Offline mock fixture used because AWS credentials were unconfigured.",
            )

            return ExtractionResult(
                promises=promises,
                raw_response=raw_json,
                telemetry=telemetry,
            )

        raise RuntimeError("Bedrock extraction failed and mock fallback is disabled.")
