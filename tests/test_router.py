"""
Unit tests for ActionRouter staging adapters.
Validates safety rules: NEVER send emails or auto-execute without confirmation.
"""

from unittest.mock import MagicMock, patch
import pytest
from src.action_router import ActionRouter


def test_todoist_simulated_mode():
    """Verify that Todoist staging gracefully simulates when token is absent."""
    router = ActionRouter(todoist_token="")
    res = router.stage_todoist("Submit architecture slides", due_date="tomorrow at 5pm")

    assert res["success"] is True
    assert res["mode"] == "SIMULATED_STAGING"
    assert "Submit architecture slides #promise-keeper" in res["message"]


def test_todoist_live_mocked():
    """Verify that Todoist live API correctly appends #promise-keeper label."""
    mock_api = MagicMock()
    mock_task = MagicMock(id="task_12345", url="https://todoist.com/showTask?id=task_12345")
    mock_api.add_task.return_value = mock_task

    router = ActionRouter(todoist_token="test_token")
    router._todoist_api = mock_api

    res = router.stage_todoist("Finish hackathon demo", due_date="today", priority=2)

    assert res["success"] is True
    assert res["mode"] == "LIVE_API"
    assert res["task_id"] == "task_12345"
    mock_api.add_task.assert_called_once_with(
        content="Finish hackathon demo #promise-keeper",
        priority=2,
        due_string="today",
    )


def test_calendar_simulated_mode():
    """Verify that Google Calendar staging simulates safely without credentials."""
    router = ActionRouter()
    res = router.stage_calendar_event(
        title="Sync with Sarah",
        start_iso="2026-10-20T17:00:00Z",
        duration_minutes=30,
    )

    assert res["success"] is True
    assert res["mode"] == "SIMULATED_STAGING"
    assert "Tentative Block" in res["message"]


def test_calendar_live_mocked_enforces_tentative():
    """Verify that Google Calendar insert strictly sets status='tentative'."""
    mock_cal = MagicMock()
    mock_events = MagicMock()
    mock_cal.events.return_value = mock_events
    mock_events.insert.return_value.execute.return_value = {
        "id": "evt_9999",
        "htmlLink": "https://calendar.google.com/event?eid=9999",
    }

    router = ActionRouter()
    router._calendar_service = mock_cal

    res = router.stage_calendar_event(
        title="Sign Vendor Agreement",
        start_iso="2026-10-21T14:30:00Z",
        duration_minutes=45,
    )

    assert res["success"] is True
    assert res["mode"] == "LIVE_API"
    assert res["event_id"] == "evt_9999"

    # Assert status='tentative' was strictly set in payload
    insert_call_args = mock_events.insert.call_args[1]
    body = insert_call_args["body"]
    assert body["status"] == "tentative"
    assert body["transparency"] == "transparent"
    assert "[Tentative Block]" in body["summary"]


def test_gmail_draft_simulated_mode():
    """Verify Gmail draft staging simulates safely without sending."""
    router = ActionRouter()
    res = router.stage_gmail_draft(
        to_email="colleague@test.com",
        subject="Pitch deck follow up",
        body="Here is the deck as discussed.",
    )

    assert res["success"] is True
    assert res["mode"] == "SIMULATED_STAGING"
    assert "colleague@test.com" in res["message"]


def test_gmail_draft_safety_never_calls_send():
    """CRITICAL SAFETY TEST: Verify that Gmail API only invokes drafts().create(), NEVER messages().send()."""
    mock_gmail = MagicMock()
    mock_users = MagicMock()
    mock_drafts = MagicMock()
    mock_messages = MagicMock()

    mock_gmail.users.return_value = mock_users
    mock_users.drafts.return_value = mock_drafts
    mock_users.messages.return_value = mock_messages

    mock_drafts.create.return_value.execute.return_value = {"id": "draft_abc123"}

    router = ActionRouter()
    router._gmail_service = mock_gmail

    res = router.stage_gmail_draft(
        to_email="sarah.lin@example.com",
        subject="Meeting followup",
        body="Attaching the slides.",
    )

    assert res["success"] is True
    assert res["mode"] == "LIVE_API"
    assert res["draft_id"] == "draft_abc123"

    # drafts.create must be called
    mock_drafts.create.assert_called_once()

    # messages.send must NEVER be called
    mock_messages.send.assert_not_called()
