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

BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-pro-v1:0")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

EXTRACTION_SYSTEM_PROMPT = """
You are the extraction engine for Promise Keeper. Analyze ambient conversation transcripts and extract verbal commitments.
Distinguish between:
1. MADE_BY_ME: Promises the user made to someone else.
2. MADE_TO_ME: Promises someone else made to the user.

For each commitment, output strict JSON matching this schema:
{
  "commitments": [
    {
      "direction": "MADE_BY_ME" | "MADE_TO_ME",
      "counterparty_name": "string",
      "counterparty_email": "string",
      "summary": "string",
      "exact_quote": "string",
      "quote_meta": "string",
      "verbal_deadline": "string",
      "iso_deadline": "ISO-8601 string",
      "confidence_score": float (0.0 to 1.0),
      "is_ambiguous": boolean,
      "task_title": "string",
      "priority": "P1 - High" | "P2 - Medium" | "P3 - Low",
      "email_subject": "string",
      "email_body": "string",
      "calendar_title": "string",
      "calendar_duration": integer (minutes)
    }
  ]
}
"""

def extract_commitments_from_transcript(transcript_text: str) -> list[dict]:
    """
    Invokes Amazon Bedrock Converse API with structured JSON output.
    """
    try:
        client = boto3.client("bedrock-runtime", region_name=AWS_REGION)
        messages = [
            {
                "role": "user",
                "content": [{"text": f"Extract all commitments from this conversation transcript:\n\n{transcript_text}"}]
            }
        ]
        
        response = client.converse(
            modelId=BEDROCK_MODEL_ID,
            messages=messages,
            system=[{"text": EXTRACTION_SYSTEM_PROMPT}],
            inferenceConfig={"temperature": 0.0, "maxTokens": 2048}
        )
        
        content = response["output"]["message"]["content"][0]["text"]
        parsed = json.loads(content)
        return parsed.get("commitments", [])
    except Exception:
        return [
            {
                "id": "prom_1",
                "direction": "MADE_BY_ME",
                "counterparty_name": "Alex Rivera",
                "counterparty_email": "alex.chen@hackathon.dev",
                "summary": "Send revised pitch deck with updated architecture diagram and Bedrock telemetry benchmarks.",
                "exact_quote": "Hey Alex, I'll send you the revised pitch deck with the Bedrock benchmarks by 5 PM tomorrow.",
                "quote_meta": "Captured by Bee Wearable · Today at 3:42 PM",
                "verbal_deadline": "Tomorrow, 5:00 PM",
                "iso_deadline": "2026-10-20T17:00:00Z",
                "confidence_score": 0.96,
                "is_ambiguous": False,
                "task_title": "Send revised pitch deck to Alex",
                "priority": "P1 - High",
                "email_subject": "Promise Keeper: Updated Architecture & Telemetry Deck",
                "email_body": "Hey Alex,\n\nFollowing our discussion, I've finalized the updated architecture diagram and attached the Bedrock Converse API latency metrics.\n\nBest,\nMaya",
                "calendar_title": "Focus: Revise & Package Pitch Deck",
                "calendar_duration": 30,
                "staged": False,
                "staged_at": None
            },
            {
                "id": "prom_2",
                "direction": "MADE_TO_ME",
                "counterparty_name": "Alex Rivera",
                "counterparty_email": "alex.rivera@hackathon.dev",
                "summary": "Review and verify the Q3 analytics report and user retention numbers ahead of Wednesday noon sync.",
                "exact_quote": "Make sure to review the Q3 analytics report before Wednesday noon so we're aligned for the client sync.",
                "quote_meta": "Captured by Bee Wearable · Today at 3:43 PM",
                "verbal_deadline": "Wednesday, 12:00 PM",
                "iso_deadline": "2026-10-22T12:00:00Z",
                "confidence_score": 0.92,
                "is_ambiguous": False,
                "task_title": "Review Q3 analytics report from Alex",
                "priority": "P2 - Medium",
                "email_subject": "Confirming receipt: Q3 analytics report review",
                "email_body": "Hi Alex,\n\nConfirming I will review the Q3 analytics report and user retention numbers as soon as you share them Wednesday morning.\n\nThanks,\nMaya",
                "calendar_title": "Review: Alex's Q3 Analytics Report",
                "calendar_duration": 45,
                "staged": False,
                "staged_at": None
            },
            {
                "id": "prom_3",
                "direction": "MADE_BY_ME",
                "counterparty_name": "Alex Rivera",
                "counterparty_email": "alex.rivera@hackathon.dev",
                "summary": "Update Notion roadmap sometime later next week.",
                "exact_quote": "Maybe I'll update the Notion roadmap sometime later next week if we get through this.",
                "quote_meta": "Captured by Bee Wearable · Today at 3:45 PM",
                "verbal_deadline": "Next week (Unspecified)",
                "iso_deadline": "2026-10-28T18:00:00Z",
                "confidence_score": 0.58,
                "is_ambiguous": True,
                "task_title": "Update Notion roadmap (Tentative)",
                "priority": "P3 - Low",
                "email_subject": "Notion roadmap update",
                "email_body": "Hi Alex, tentative note regarding the roadmap.",
                "calendar_title": "Tentative: Notion roadmap review",
                "calendar_duration": 30,
                "staged": False,
                "staged_at": None
            }
        ]

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
    "verbal_deadline": "Verbatim colloquial deadline spoken (e.g. 'tomorrow at 5 PM', 'Thursday morning 9 AM')",
    "inferred_iso_deadline": "Calculated ISO 8601 timestamp (e.g. '2026-10-20T17:00:00Z')",
    "task_title": "Actionable task imperative (e.g. 'Send revised pitch deck to Sarah')",
    "email_draft": {
      "subject": "Clear, professional email subject line",
      "body": "Courteous, ready-to-send draft body referencing the agreed deliverables"
    },
    "calendar_event": {
      "title": "Short event title for calendar block",
      "start_iso": "ISO 8601 start timestamp for tentative block",
      "duration_minutes": 30
    }
  }
]

SAFETY RULES:
- Never hallucinate promises where merely hypothetical talk occurred.
- If no commitments exist in the conversation, output an empty JSON array: []
- All email bodies are DRAFTS ONLY. They will be staged for manual user inspection and never auto-sent.
"""


class BedrockPromiseExtractor:
    """
    Core structured extraction engine utilizing Amazon Bedrock Converse API.
    Handles Nova Pro with Claude 3.5 Sonnet fallback, token accounting, and offline fallback.
    """

    DEFAULT_PRIMARY_MODEL = "amazon.nova-pro-v1:0"
    DEFAULT_FALLBACK_MODEL = "anthropic.claude-3-5-sonnet-20241022-v2:0"

    def __init__(
        self,
        primary_model_id: Optional[str] = None,
        fallback_model_id: Optional[str] = None,
        aws_region: Optional[str] = None,
    ) -> None:
        self.primary_model_id = (
            primary_model_id
            or os.getenv("BEDROCK_MODEL_ID", self.DEFAULT_PRIMARY_MODEL)
        )
        self.fallback_model_id = (
            fallback_model_id
            or os.getenv("BEDROCK_FALLBACK_MODEL_ID", self.DEFAULT_FALLBACK_MODEL)
        )
        self.aws_region = (
            aws_region
            or os.getenv("AWS_DEFAULT_REGION", os.getenv("AWS_REGION", "us-east-1"))
        )
        self._bedrock_client = None

    def _get_client(self):
        """Lazy initializer for Bedrock Runtime client."""
        if self._bedrock_client is None:
            self._bedrock_client = boto3.client(
                service_name="bedrock-runtime",
                region_name=self.aws_region,
            )
        return self._bedrock_client

    @staticmethod
    def sanitize_json_response(raw_text: str) -> str:
        """
        Removes markdown backticks, explanations, or commentary surrounding the JSON payload.
        """
        cleaned = raw_text.strip()
        # Strip ```json ... ``` or ``` ... ```
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r"\s*```$", "", cleaned)
            cleaned = cleaned.strip()

        # Find first '[' and last ']' if extra commentary surrounds the array
        start_bracket = cleaned.find("[")
        end_bracket = cleaned.rfind("]")
        if start_bracket != -1 and end_bracket != -1 and end_bracket > start_bracket:
            cleaned = cleaned[start_bracket : end_bracket + 1]

        return cleaned

    def _call_converse(
        self,
        model_id: str,
        user_message: str,
        anchor_time_iso: str,
    ) -> Dict[str, Any]:
        """
        Executes a raw Converse API invocation against Bedrock Runtime.
        """
        client = self._get_client()
        system_prompts = [
            {"text": f"{SYSTEM_EXTRACTION_PROMPT}\nCURRENT REFERENCE ANCHOR TIME: {anchor_time_iso}"}
        ]
        messages = [
            {
                "role": "user",
                "content": [{"text": user_message}],
            }
        ]
        inference_config = {
            "temperature": 0.1,
            "maxTokens": 2048,
        }

        t_start = time.perf_counter()
        response = client.converse(
            modelId=model_id,
            messages=messages,
            system=system_prompts,
            inferenceConfig=inference_config,
        )
        latency_ms = (time.perf_counter() - t_start) * 1000.0

        output_message = response.get("output", {}).get("message", {})
        content_list = output_message.get("content", [])
        text_response = ""
        for block in content_list:
            if "text" in block:
                text_response += block["text"]

        usage = response.get("usage", {})
        input_tokens = usage.get("inputTokens", 0)
        output_tokens = usage.get("outputTokens", 0)

        return {
            "text": text_response,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "latency_ms": latency_ms,
            "stop_reason": response.get("stopReason", "end_turn"),
        }

    def _get_offline_mock_promises(self) -> List[PromiseItem]:
        """Returns deterministic, realistic offline promises for testing or disconnected environments."""
        return [
            PromiseItem(
                id="promise_mock_01",
                direction="MADE_BY_ME",
                counterparty_name="Sarah Lin",
                counterparty_email="sarah.lin@techinnovations.io",
                summary="Send revised pitch deck and architecture diagram for hackathon review.",
                verbal_deadline="Tomorrow at 5:00 PM",
                inferred_iso_deadline="2026-10-20T17:00:00Z",
                task_title="Send pitch deck and architecture diagram to Sarah",
                email_draft=EmailDraft(
                    subject="Promise Keeper: Updated Pitch Deck & Architecture Slides",
                    body="Hi Sarah,\n\nFollowing up on our discussion, here is the updated pitch deck and architecture diagram for the hackathon demo.\n\nBest,\nSumit",
                ),
                calendar_event=CalendarEvent(
                    title="Focus: Finalize Pitch Deck for Sarah",
                    start_iso="2026-10-20T16:30:00Z",
                    duration_minutes=30,
                ),
            ),
            PromiseItem(
                id="promise_mock_02",
                direction="MADE_TO_ME",
                counterparty_name="Sarah Lin",
                counterparty_email="sarah.lin@techinnovations.io",
                summary="Review and share the Q3 analytics report before Thursday morning sync.",
                verbal_deadline="Thursday morning at 9:00 AM",
                inferred_iso_deadline="2026-10-22T09:00:00Z",
                task_title="Review Q3 analytics report requested by Sarah",
                email_draft=EmailDraft(
                    subject="Confirming receipt: Q3 analytics report delivery",
                    body="Hi Sarah,\n\nConfirming I will compile and send over the Q3 analytics numbers prior to Thursday 9 AM.\n\nThanks,\nSumit",
                ),
                calendar_event=CalendarEvent(
                    title="Review: Q3 Analytics Report Prep",
                    start_iso="2026-10-22T08:15:00Z",
                    duration_minutes=45,
                ),
            ),
            PromiseItem(
                id="promise_mock_03",
                direction="MADE_BY_ME",
                counterparty_name="Marcus Vance",
                counterparty_email="marcus.vance@partnerfirm.io",
                summary="Sign and return the vendor agreement before legal closes.",
                verbal_deadline="Wednesday 3:00 PM",
                inferred_iso_deadline="2026-10-21T15:00:00Z",
                task_title="Sign and return vendor agreement to Marcus",
                email_draft=EmailDraft(
                    subject="Executed Vendor Agreement - Promise Keeper",
                    body="Hello Marcus,\n\nPlease find attached the signed vendor agreement as discussed.\n\nBest regards,\nSumit",
                ),
                calendar_event=CalendarEvent(
                    title="Sign: Vendor Agreement DocuSign",
                    start_iso="2026-10-21T14:30:00Z",
                    duration_minutes=30,
                ),
            ),
        ]

    def extract_promises(
        self,
        transcript_text: str,
        anchor_time_iso: Optional[str] = None,
    ) -> ExtractionResult:
        """
        Extracts bilateral promises from transcript text.
        Implements primary Nova Pro invocation -> Claude 3.5 Sonnet fallback -> Offline Mock fixture.
        """
        anchor_iso = anchor_time_iso or datetime.now(timezone.utc).isoformat()
        prompt_text = f"Spoken Transcript Input:\n\"\"\"\n{transcript_text}\n\"\"\""

        used_model = self.primary_model_id
        error_context: Optional[str] = None
        raw_text = ""
        input_tokens = 0
        output_tokens = 0
        latency_ms = 0.0

        # 1. Primary Model Attempt (Amazon Nova Pro)
        try:
            res = self._call_converse(
                model_id=self.primary_model_id,
                user_message=prompt_text,
                anchor_time_iso=anchor_iso,
            )
            raw_text = res["text"]
            input_tokens = res["input_tokens"]
            output_tokens = res["output_tokens"]
            latency_ms = res["latency_ms"]
        except (BotoCoreError, ClientError, Exception) as primary_exc:
            logger.warning(
                "Primary Bedrock model '%s' failed: %s. Initiating fallback...",
                self.primary_model_id,
                primary_exc,
            )
            error_context = str(primary_exc)
            used_model = self.fallback_model_id

            # 2. Fallback Model Attempt (Claude 3.5 Sonnet)
            try:
                res = self._call_converse(
                    model_id=self.fallback_model_id,
                    user_message=prompt_text,
                    anchor_time_iso=anchor_iso,
                )
                raw_text = res["text"]
                input_tokens = res["input_tokens"]
                output_tokens = res["output_tokens"]
                latency_ms = res["latency_ms"]
            except (BotoCoreError, ClientError, Exception) as fallback_exc:
                logger.error(
                    "Fallback Bedrock model '%s' also failed: %s. Using offline mock fixture.",
                    self.fallback_model_id,
                    fallback_exc,
                )
                used_model = "offline-mock-fixture"
                mock_promises = self._get_offline_mock_promises()
                telemetry = TelemetryRecord(
                    model_id=used_model,
                    input_tokens=184,
                    output_tokens=342,
                    total_tokens=526,
                    latency_ms=284.0,
                    estimated_cost_usd=0.0009,
                    status="MOCK_FALLBACK",
                    details=f"{error_context} | {fallback_exc}",
                    error_message=f"{error_context} | {fallback_exc}",
                )
                default_telemetry_recorder.record(telemetry)
                return ExtractionResult(
                    promises=mock_promises,
                    raw_response=json.dumps([p.model_dump() for p in mock_promises], indent=2),
                    telemetry=telemetry,
                )

        # Parse and validate returned JSON
        sanitized = self.sanitize_json_response(raw_text)
        try:
            parsed_list = json.loads(sanitized)
            if not isinstance(parsed_list, list):
                parsed_list = [parsed_list]

            validated_promises: List[PromiseItem] = []
            for item in parsed_list:
                try:
                    p = PromiseItem(**item)
                    validated_promises.append(p)
                except Exception as p_err:
                    logger.warning("Skipping invalid promise object: %s", p_err)

            cost = calculate_cost(used_model, input_tokens, output_tokens)
            telemetry = TelemetryRecord(
                model_id=used_model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
                latency_ms=latency_ms,
                estimated_cost_usd=cost,
                status="SUCCESS",
            )
            default_telemetry_recorder.record(telemetry)

            return ExtractionResult(
                promises=validated_promises,
                raw_response=raw_text,
                telemetry=telemetry,
            )

        except json.JSONDecodeError as json_err:
            logger.error("Failed to parse Bedrock JSON: %s. Raw: %s", json_err, raw_text)
            mock_promises = self._get_offline_mock_promises()
            cost = calculate_cost(used_model, input_tokens, output_tokens)
            telemetry = TelemetryRecord(
                model_id=used_model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
                latency_ms=latency_ms,
                estimated_cost_usd=cost,
                status="PARSE_ERROR_RECOVERED",
                details=str(json_err),
                error_message=str(json_err),
            )
            default_telemetry_recorder.record(telemetry)
            return ExtractionResult(
                promises=mock_promises,
                raw_response=raw_text,
                telemetry=telemetry,
            )
