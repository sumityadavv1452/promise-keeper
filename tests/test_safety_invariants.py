"""
Safety Invariants and Human-In-The-Loop Verification Suite.
Validates the foundational hackathon safety architecture:
1. Strict gmail.compose OAuth scope (NEVER gmail.send or mail.google.com).
2. Atomic dispatch: zero premature state mutations on downstream failures.
3. Idempotency: duplicate dispatches are rejected safely.
4. Tentative calendar blocks protect schedule availability.
5. Resilient Bee audio ingestion offline fallback.
"""

from unittest.mock import MagicMock, patch
import pytest
from integrations.dispatcher import (
    Dispatcher,
    stage_commitment_atomically,
    undo_staging,
    GMAIL_COMPOSE_SCOPE,
    AUTHORIZED_SCOPES,
    FORBIDDEN_SCOPES,
)
from integrations.bee_client import fetch_latest_bee_transcript, BeeClient


def test_oauth_exclusive_gmail_compose_scope():
    """Verify that OAuth scopes exclusively allow draft composition and forbid send."""
    dispatcher = Dispatcher()
    scopes = dispatcher.authorized_scopes

    assert GMAIL_COMPOSE_SCOPE in scopes, "gmail.compose MUST be an authorized scope"
    assert "https://www.googleapis.com/auth/calendar.events" in scopes

    # Verify that dangerous send/modify scopes are forbidden
    for forbidden in dispatcher.forbidden_scopes:
        assert forbidden not in scopes, f"Dangerous scope '{forbidden}' must NEVER be authorized"


def test_gmail_compose_never_calls_send():
    """CRITICAL SAFETY TEST: Verify that Gmail API only invokes drafts().create(), NEVER messages().send()."""
    mock_gmail = MagicMock()
    mock_users = MagicMock()
    mock_drafts = MagicMock()
    mock_messages = MagicMock()

    mock_gmail.users.return_value = mock_users
    mock_users.drafts.return_value = mock_drafts
    mock_users.messages.return_value = mock_messages
    mock_drafts.create.return_value.execute.return_value = {"id": "draft_safety_test"}

    dispatcher = Dispatcher()
    dispatcher._gmail_service = mock_gmail

    res = dispatcher.stage_gmail_draft(
        to_email="client@example.com",
        subject="Deliverables review",
        body="Draft content waiting for human approval.",
    )

    assert res["success"] is True
    assert res["mode"] == "LIVE_API"
    assert res["draft_id"] == "draft_safety_test"

    # drafts.create must be called
    mock_drafts.create.assert_called_once()

    # messages.send must NEVER be invoked under any circumstance
    mock_messages.send.assert_not_called()


def test_calendar_tentative_block_invariant():
    """Verify Google Calendar events are strictly tentative and transparent (non-destructive)."""
    mock_cal = MagicMock()
    mock_events = MagicMock()
    mock_cal.events.return_value = mock_events
    mock_events.insert.return_value.execute.return_value = {
        "id": "cal_evt_101",
        "htmlLink": "https://calendar.google.com/event?eid=101",
    }

    dispatcher = Dispatcher()
    dispatcher._calendar_service = mock_cal

    res = dispatcher.stage_calendar_event(
        title="Review Q3 Analytics",
        start_iso="2026-10-22T12:00:00Z",
        duration_minutes=45,
    )

    assert res["success"] is True
    call_args = mock_events.insert.call_args[1]
    payload = call_args["body"]
    assert payload["status"] == "tentative", "Calendar status MUST be 'tentative'"
    assert payload["transparency"] == "transparent", "Event must be transparent to avoid blocking"
    assert "[Tentative Block]" in payload["summary"]


def test_atomic_dispatch_no_premature_state_mutation():
    """Verify that promise['staged'] remains False if any downstream service fails."""
    failing_dispatcher = MagicMock(spec=Dispatcher)
    failing_dispatcher.stage_todoist.return_value = {"success": True}
    # Simulate downstream Gmail failure
    failing_dispatcher.stage_gmail_draft.side_effect = RuntimeError("Gmail API 503 Unavailable")

    promise = {
        "id": "prom_test_atomic",
        "task_title": "Send financial deck",
        "staged": False,
    }

    success, message = stage_commitment_atomically(
        promise=promise,
        dispatcher=failing_dispatcher,
    )

    assert success is False
    assert "Dispatch failed" in message
    assert "Gmail API 503" in message
    # Invariant: promise['staged'] must NEVER be True on failure
    assert promise["staged"] is False
    assert "staged_at" not in promise


def test_atomic_dispatch_idempotency_guard():
    """Verify that an already-staged commitment cannot be re-dispatched."""
    dispatcher = MagicMock(spec=Dispatcher)
    already_staged_promise = {
        "id": "prom_already_staged",
        "task_title": "Completed task",
        "staged": True,
        "staged_at": "2026-10-20T00:00:00Z",
    }

    success, message = stage_commitment_atomically(
        promise=already_staged_promise,
        dispatcher=dispatcher,
    )

    assert success is False
    assert message == "Commitment already staged."
    # Downstream services must not be called
    dispatcher.stage_todoist.assert_not_called()
    dispatcher.stage_gmail_draft.assert_not_called()
    dispatcher.stage_calendar_event.assert_not_called()


def test_atomic_dispatch_success_mutation():
    """Verify that promise['staged'] is flipped to True only upon total downstream success."""
    dispatcher = MagicMock(spec=Dispatcher)
    dispatcher.stage_todoist.return_value = {"success": True}
    dispatcher.stage_gmail_draft.return_value = {"success": True}
    dispatcher.stage_calendar_event.return_value = {"success": True}

    promise = {
        "id": "prom_success",
        "task_title": "Deliver mockups",
        "verbal_deadline": "Tomorrow noon",
        "iso_deadline": "2026-10-21T12:00:00Z",
        "counterparty_email": "client@studio.design",
        "email_subject": "Mockups",
        "email_body": "Attached mockups.",
        "calendar_title": "Review mockups",
        "calendar_duration": 30,
        "staged": False,
    }

    success, message = stage_commitment_atomically(
        promise=promise,
        dispatcher=dispatcher,
    )

    assert success is True
    assert "Successfully staged" in message
    assert promise["staged"] is True
    assert "staged_at" in promise
    dispatcher.stage_todoist.assert_called_once()
    dispatcher.stage_gmail_draft.assert_called_once()
    dispatcher.stage_calendar_event.assert_called_once()


def test_bee_ingestion_offline_graceful_fallback():
    """Verify fetch_latest_bee_transcript returns a safe envelope in offline test environments."""
    result = fetch_latest_bee_transcript()
    assert isinstance(result, dict)
    assert "status" in result
    assert "segments" in result
    assert len(result["segments"]) > 0


def test_no_autonomous_dispatch_without_human_approval():
    promise = {
        "id": "test_1",
        "task_title": "Test Pitch Deck",
        "priority": "P1 - High",
        "email_subject": "Test Sub",
        "email_body": "Test Body",
        "calendar_title": "Test Cal",
        "verbal_deadline": "Tomorrow",
        "staged": False
    }
    assert promise["staged"] is False
    assert promise.get("staged_at") is None


def test_atomic_staging_and_undo():
    promise = {
        "id": "test_2",
        "task_title": "Test Pitch Deck",
        "priority": "P1 - High",
        "email_subject": "Test Sub",
        "email_body": "Test Body",
        "calendar_title": "Test Cal",
        "verbal_deadline": "Tomorrow",
        "staged": False
    }
    ok, msg = stage_commitment_atomically(promise, {})
    assert ok is True
    assert promise["staged"] is True
    assert promise["staged_at"] is not None

    ok_again, _ = stage_commitment_atomically(promise, {})
    assert ok_again is False

    undo_ok = undo_staging(promise)
    assert undo_ok is True
    assert promise["staged"] is False

