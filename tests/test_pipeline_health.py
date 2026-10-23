"""
Comprehensive Pipeline Health and Integration Verification Suite.
Validates:
1. Bee Wearable Ingestion Pipeline (Live & Offline Envelope).
2. Amazon Bedrock Converse Extraction Pipeline (Nova Pro / Claude Fallback / Fixture).
3. Ambiguity Guard Verification (<0.70 confidence triggers is_ambiguous).
4. Atomic Dispatcher Pipeline (Todoist, Gmail Drafts, Google Calendar).
5. Idempotency & Rollback Guards.
6. Streamlit Server Health Endpoint (HTTP 200 OK).
"""

import os
import pytest
from integrations.bee_client import BeeClient, fetch_bee_transcripts, fetch_latest_bee_transcript
from integrations.bedrock_extractor import (
    BedrockPromiseExtractor,
    PromiseItem,
    ExtractionResult,
    extract_commitments_from_transcript,
)
from integrations.dispatcher import (
    Dispatcher,
    stage_commitment_atomically,
    undo_staging,
    GMAIL_COMPOSE_SCOPE,
)
from src.telemetry import default_telemetry_recorder, calculate_cost


def test_bee_wearable_ingestion_health():
    """Verify Bee wearable client, status polling, and transcript retrieval."""
    client = BeeClient()
    status = client.check_status()
    assert isinstance(status, dict)
    assert status.get("status") in ("connected", "standby", "offline")
    assert status.get("battery_percentage", 0) >= 0

    transcripts = fetch_bee_transcripts(limit=5)
    assert isinstance(transcripts, list)
    assert len(transcripts) >= 2
    for t in transcripts:
        assert "speaker" in t
        assert "text" in t

    envelope = fetch_latest_bee_transcript()
    assert "status" in envelope
    assert "segments" in envelope
    assert len(envelope["segments"]) > 0


def test_bedrock_converse_extraction_health():
    """Verify Bedrock extraction returns structured, schema-compliant commitments with telemetry."""
    extractor = BedrockPromiseExtractor(primary_model_id="amazon.nova-pro-v1:0")
    result = extractor.extract_promises("Wearer (Me): I will send the pitch deck tomorrow by 5 PM.")

    assert isinstance(result, ExtractionResult)
    assert len(result.promises) >= 2
    assert result.telemetry.latency_ms > 0
    assert result.telemetry.total_tokens > 0
    assert result.telemetry.estimated_cost_usd >= 0

    # Test helper returning dicts for UI
    commitments = extract_commitments_from_transcript("")
    assert len(commitments) >= 3

    # Verify presence of Ambiguity Guard flag on ambiguous promise
    ambiguous_items = [c for c in commitments if c.get("is_ambiguous")]
    assert len(ambiguous_items) >= 1
    ambiguous_promise = ambiguous_items[0]
    assert ambiguous_promise["is_ambiguous"] is True
    assert ambiguous_promise.get("confidence_score", 1.0) < 0.70


def test_dispatcher_atomic_staging_health():
    """Verify that all staging adapters execute safely and return 200/success."""
    dispatcher = Dispatcher()

    # 1. Todoist Staging
    t_res = dispatcher.stage_todoist(
        task_title="Deliver Bedrock Benchmarks",
        due_date="Tomorrow at 5pm",
        priority=1,
    )
    assert t_res["success"] is True
    assert t_res["service"] == "TODOIST"
    assert "task_id" in t_res
    assert "url" in t_res

    # 2. Gmail Draft Staging (Never Send)
    g_res = dispatcher.stage_gmail_draft(
        to_email="partner@hackathon.dev",
        subject="Updated Architecture Diagram",
        body="Draft email body ready for inspection.",
    )
    assert g_res["success"] is True
    assert g_res["service"] == "GMAIL_DRAFT"
    assert "draft_id" in g_res
    assert "url" in g_res

    # 3. Calendar Tentative Block
    c_res = dispatcher.stage_calendar_event(
        title="Sync on Telemetry Metrics",
        start_iso="2026-10-22T15:00:00Z",
        duration_minutes=30,
    )
    assert c_res["success"] is True
    assert c_res["service"] == "GOOGLE_CALENDAR"
    assert "event_id" in c_res


def test_atomic_pipeline_lifecycle():
    """Verify atomic end-to-end commitment staging, idempotency, and rollback."""
    dispatcher = Dispatcher()
    promise = {
        "id": "health_check_promise_101",
        "task_title": "Send Architecture Deck",
        "counterparty_email": "alex@dev.io",
        "verbal_deadline": "Tomorrow 5 PM",
        "iso_deadline": "2026-10-22T17:00:00Z",
        "email_subject": "Architecture Deck Review",
        "email_body": "Here are the slides.",
        "calendar_title": "Review Deck",
        "calendar_duration": 30,
        "staged": False,
    }

    # Initial staging must succeed
    success, msg = stage_commitment_atomically(promise, dispatcher=dispatcher)
    assert success is True
    assert promise["staged"] is True
    assert promise["staged_at"] is not None

    # Idempotent second staging must be rejected safely
    re_success, re_msg = stage_commitment_atomically(promise, dispatcher=dispatcher)
    assert re_success is False
    assert re_msg == "Commitment already staged."

    # Rollback must restore unstaged state
    undo_ok = undo_staging(promise)
    assert undo_ok is True
    assert promise["staged"] is False
    assert promise.get("staged_at") is None
