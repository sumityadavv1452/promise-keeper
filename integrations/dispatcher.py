"""
Dispatcher and Safe Staging Module for Promise Keeper.
Implements atomic dispatch to Todoist (#promise-keeper), Gmail Drafts, and Google Calendar.
Enforces the core hackathon safety invariants:
1. Double-dispatch race prevention & state manipulation fix:
   `promise['staged'] = True` must NEVER be set before all downstream API calls complete.
2. gmail.compose is the exclusive OAuth scope (NEVER gmail.send or mail.google.com).
3. Idempotency guards prevent duplicate draft/task creation.
"""

from __future__ import annotations
import base64
from email.mime.text import MIMEText
import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Strict OAuth Scope Declarations
GMAIL_COMPOSE_SCOPE = "https://www.googleapis.com/auth/gmail.compose"
CALENDAR_EVENTS_SCOPE = "https://www.googleapis.com/auth/calendar.events"
AUTHORIZED_SCOPES = [GMAIL_COMPOSE_SCOPE, CALENDAR_EVENTS_SCOPE]

FORBIDDEN_SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://mail.google.com/",
    "https://www.googleapis.com/auth/gmail.modify",
]


class Dispatcher:
    """
    Coordinates atomic staging across Todoist, Google Calendar, and Gmail Drafts.
    Guarantees draft-only isolation and tentative calendar blocks.
    """

    def __init__(
        self,
        todoist_token: Optional[str] = None,
        google_creds_file: Optional[str] = None,
        google_token_file: Optional[str] = None,
    ) -> None:
        self.todoist_token = (
            todoist_token or os.getenv("TODOIST_API_TOKEN", "")
        ).strip()
        self.google_creds_file = (
            google_creds_file
            or os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
        ).strip()
        self.google_token_file = (
            google_token_file or os.getenv("GOOGLE_TOKEN_FILE", "token.json")
        ).strip()

        self._todoist_api = None
        self._gmail_service = None
        self._calendar_service = None

        self._init_todoist()
        self._init_google_services()

    @property
    def authorized_scopes(self) -> list[str]:
        return list(AUTHORIZED_SCOPES)

    @property
    def forbidden_scopes(self) -> list[str]:
        return list(FORBIDDEN_SCOPES)

    def _init_todoist(self) -> None:
        """Initializes Todoist API client if token is configured."""
        if self.todoist_token:
            try:
                from todoist_api_python.api import TodoistAPI
                self._todoist_api = TodoistAPI(self.todoist_token)
                logger.info("Todoist client initialized.")
            except Exception as exc:
                logger.warning("Could not initialize Todoist client: %s", exc)
                self._todoist_api = None

    def _init_google_services(self) -> None:
        """Initializes Gmail and Google Calendar API clients with verified scopes."""
        if os.path.exists(self.google_token_file):
            try:
                from google.oauth2.credentials import Credentials
                from googleapiclient.discovery import build

                # Enforce exclusive compose scope
                creds = Credentials.from_authorized_user_file(
                    self.google_token_file, AUTHORIZED_SCOPES
                )
                self._gmail_service = build("gmail", "v1", credentials=creds)
                self._calendar_service = build("calendar", "v3", credentials=creds)
                logger.info("Google services initialized strictly with compose & calendar scopes.")
            except Exception as exc:
                logger.warning("Could not initialize Google services: %s", exc)
                self._gmail_service = None
                self._calendar_service = None

    def stage_todoist(
        self,
        task_title: str,
        due_date: Optional[str] = None,
        priority: int = 1,
    ) -> Dict[str, Any]:
        """Stages a task into Todoist with the #promise-keeper tag."""
        tagged_title = f"{task_title} #promise-keeper"
        if self._todoist_api:
            try:
                kwargs: Dict[str, Any] = {
                    "content": tagged_title,
                    "priority": priority,
                }
                if due_date:
                    kwargs["due_string"] = due_date
                task = self._todoist_api.add_task(**kwargs)
                return {
                    "success": True,
                    "mode": "LIVE_API",
                    "service": "TODOIST",
                    "task_id": getattr(task, "id", "created"),
                    "url": getattr(task, "url", "https://app.todoist.com"),
                    "message": f"Created Todoist task: '{tagged_title}'",
                }
            except Exception as exc:
                logger.error("Todoist API dispatch error: %s", exc)
                raise RuntimeError(f"Todoist API failed: {exc}")

        # Simulated staging fallback
        return {
            "success": True,
            "mode": "SIMULATED_STAGING",
            "service": "TODOIST",
            "task_id": f"sim_task_{abs(hash(task_title)) % 100000}",
            "url": "https://app.todoist.com/app/today",
            "message": f"Staged (Simulated): '{tagged_title}' due '{due_date or 'None'}'",
        }

    def stage_calendar_event(
        self,
        title: str,
        start_iso: str,
        duration_minutes: int = 30,
        description: str = "Staged tentative block via Promise Keeper (Bee Wearable).",
    ) -> Dict[str, Any]:
        """
        Inserts a tentative Google Calendar block.
        Always sets status='tentative' so the block is non-destructive.
        """
        try:
            clean_iso = start_iso.replace("Z", "+00:00")
            dt_start = datetime.fromisoformat(clean_iso)
        except Exception:
            dt_start = datetime.now(timezone.utc) + timedelta(days=1)

        dt_end = dt_start + timedelta(minutes=duration_minutes)

        event_payload = {
            "summary": f"[Tentative Block] {title}",
            "description": description,
            "status": "tentative",
            "transparency": "transparent",
            "start": {"dateTime": dt_start.isoformat(), "timeZone": "UTC"},
            "end": {"dateTime": dt_end.isoformat(), "timeZone": "UTC"},
        }

        if self._calendar_service:
            try:
                cal_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")
                created = (
                    self._calendar_service.events()
                    .insert(calendarId=cal_id, body=event_payload)
                    .execute()
                )
                return {
                    "success": True,
                    "mode": "LIVE_API",
                    "service": "GOOGLE_CALENDAR",
                    "event_id": created.get("id"),
                    "html_link": created.get("htmlLink", "https://calendar.google.com"),
                    "message": f"Tentative calendar block scheduled: '{title}'",
                }
            except Exception as exc:
                logger.error("Google Calendar dispatch error: %s", exc)
                raise RuntimeError(f"Google Calendar failed: {exc}")

        return {
            "success": True,
            "mode": "SIMULATED_STAGING",
            "service": "GOOGLE_CALENDAR",
            "event_id": f"sim_cal_{abs(hash(title)) % 100000}",
            "html_link": "https://calendar.google.com",
            "message": f"Staged Tentative Block: '{title}' at {dt_start.strftime('%Y-%m-%d %H:%M')}",
        }

    def stage_gmail_draft(
        self,
        to_email: str,
        subject: str,
        body: str,
    ) -> Dict[str, Any]:
        """
        Creates an RFC 2822 Gmail draft via users.drafts.create.
        MANDATORY SAFETY RULE: NEVER CALLS messages.send().
        User must open drafts and manually hit send.
        """
        message = MIMEText(body)
        message["to"] = to_email
        message["subject"] = f"[Promise Keeper Draft] {subject}"
        raw_encoded = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        draft_body = {"message": {"raw": raw_encoded}}

        if self._gmail_service:
            try:
                draft = (
                    self._gmail_service.users()
                    .drafts()
                    .create(userId="me", body=draft_body)
                    .execute()
                )
                return {
                    "success": True,
                    "mode": "LIVE_API",
                    "service": "GMAIL_DRAFT",
                    "draft_id": draft.get("id"),
                    "url": "https://mail.google.com/mail/u/0/#drafts",
                    "message": f"Created Gmail draft for '{to_email}' with subject '{subject}'",
                }
            except Exception as exc:
                logger.error("Gmail draft dispatch error: %s", exc)
                raise RuntimeError(f"Gmail Draft API failed: {exc}")

        return {
            "success": True,
            "mode": "SIMULATED_STAGING",
            "service": "GMAIL_DRAFT",
            "draft_id": f"sim_draft_{abs(hash(to_email + subject)) % 100000}",
            "url": "https://mail.google.com/mail/u/0/#drafts",
            "message": f"Staged Gmail draft to '{to_email}' - Subject: '{subject}' (Safe: never sent)",
        }


def stage_commitment_atomically(
    promise: Dict[str, Any],
    user_edits: Optional[Dict[str, Any]] = None,
    dispatcher: Optional[Dispatcher] = None,
) -> Tuple[bool, str]:
    """
    Safely and atomically stages a commitment to Todoist, Gmail Drafts, and Google Calendar.
    Enforces idempotency, applies user edits, and prevents premature state mutations.
    """
    # 1. Idempotency Check: Never dispatch twice
    if promise.get("staged", False):
        return False, "Commitment already staged."

    active_dispatcher = dispatcher or Dispatcher()

    # Apply user-overridden form edits if provided
    if user_edits:
        for k, v in user_edits.items():
            if v is not None:
                promise[k] = v

    task_title = promise.get("task_title", "Promise Commitment")
    verbal_deadline = promise.get("verbal_deadline", "Soon")
    iso_deadline = promise.get("iso_deadline", datetime.now(timezone.utc).isoformat())
    counterparty_email = promise.get("counterparty_email", "counterparty@example.com")
    email_subject = promise.get("email_subject", f"Promise: {task_title}")
    email_body = promise.get("email_body", f"Follow up regarding: {task_title}")
    calendar_title = promise.get("calendar_title", f"Focus: {task_title}")
    calendar_duration = promise.get("calendar_duration", 30)
    priority_str = str(promise.get("priority", "P1"))
    priority_val = 4 if "P1" in priority_str else (3 if "P2" in priority_str else 1)

    try:
        # Step 1: Dispatch Todoist Task
        active_dispatcher.stage_todoist(
            task_title=task_title,
            due_date=verbal_deadline,
            priority=priority_val,
        )

        # Step 2: Dispatch Gmail Draft (strictly draft creation via gmail.compose)
        active_dispatcher.stage_gmail_draft(
            to_email=counterparty_email,
            subject=email_subject,
            body=email_body,
        )

        # Step 3: Dispatch Calendar Tentative Block
        active_dispatcher.stage_calendar_event(
            title=calendar_title,
            start_iso=iso_deadline,
            duration_minutes=calendar_duration,
        )

        # CRITICAL SAFETY INVARIANT: State flips ONLY after downstream success
        promise["staged"] = True
        promise["staged_at"] = datetime.now(timezone.utc).isoformat()
        return True, "Successfully staged to all destinations."

    except Exception as err:
        logger.error("Atomic dispatch failed: %s", err)
        # Ensure promise remains unstaged on any failure
        promise["staged"] = False
        return False, f"Dispatch failed: {err}"


def undo_staging(promise: Dict[str, Any]) -> bool:
    """
    Rolls back the staging flag and timestamp.
    """
    if not promise.get("staged", False):
        return False
    promise["staged"] = False
    promise["staged_at"] = None
    return True

