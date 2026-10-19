"""
Action Router module for Promise Keeper.
Implements staging adapters for Google Calendar, Todoist, and Gmail drafts.
Enforces the core hackathon safety invariant: NEVER send emails or auto-execute tasks without one-tap user confirmation.
"""

from __future__ import annotations
import base64
from email.mime.text import MIMEText
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class ActionRouter:
    """
    Coordinates safe staging across productivity services.
    Includes simulated staging fallbacks when third-party API credentials are not set.
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

    def _init_todoist(self) -> None:
        """Initializes Todoist API client if token is available."""
        if self.todoist_token:
            try:
                from todoist_api_python.api import TodoistAPI

                self._todoist_api = TodoistAPI(self.todoist_token)
                logger.info("Todoist API client initialized.")
            except Exception as exc:
                logger.warning("Could not initialize Todoist API: %s", exc)
                self._todoist_api = None

    def _init_google_services(self) -> None:
        """Initializes Gmail and Google Calendar API clients if token exists."""
        if os.path.exists(self.google_token_file):
            try:
                from google.oauth2.credentials import Credentials
                from googleapiclient.discovery import build

                scopes = [
                    "https://www.googleapis.com/auth/gmail.compose",
                    "https://www.googleapis.com/auth/calendar.events",
                ]
                creds = Credentials.from_authorized_user_file(
                    self.google_token_file, scopes
                )
                self._gmail_service = build("gmail", "v1", credentials=creds)
                self._calendar_service = build("calendar", "v3", credentials=creds)
                logger.info("Google services initialized with token.")
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
        """
        Stages a task into Todoist with the #promise-keeper tag.
        Falls back to a simulated staging confirmation if token is missing.
        """
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
                logger.error("Error creating Todoist task: %s", exc)
                return {
                    "success": False,
                    "mode": "LIVE_API_ERROR",
                    "service": "TODOIST",
                    "error": str(exc),
                }

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
        # Parse or default start/end times
        try:
            # Handle ISO string with trailing Z or timezone offset
            clean_iso = start_iso.replace("Z", "+00:00")
            dt_start = datetime.fromisoformat(clean_iso)
        except Exception:
            dt_start = datetime.now() + timedelta(days=1)

        dt_end = dt_start + timedelta(minutes=duration_minutes)

        event_payload = {
            "summary": f"[Tentative Block] {title}",
            "description": description,
            "status": "tentative",
            "transparency": "transparent",
            "start": {
                "dateTime": dt_start.isoformat(),
                "timeZone": "UTC",
            },
            "end": {
                "dateTime": dt_end.isoformat(),
                "timeZone": "UTC",
            },
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
                logger.error("Error creating Google Calendar event: %s", exc)
                return {
                    "success": False,
                    "mode": "LIVE_API_ERROR",
                    "service": "GOOGLE_CALENDAR",
                    "error": str(exc),
                }

        # Simulated staging fallback
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
                logger.error("Error creating Gmail draft: %s", exc)
                return {
                    "success": False,
                    "mode": "LIVE_API_ERROR",
                    "service": "GMAIL_DRAFT",
                    "error": str(exc),
                }

        # Simulated staging fallback
        return {
            "success": True,
            "mode": "SIMULATED_STAGING",
            "service": "GMAIL_DRAFT",
            "draft_id": f"sim_draft_{abs(hash(to_email + subject)) % 100000}",
            "url": "https://mail.google.com/mail/u/0/#drafts",
            "message": f"Staged Gmail draft to '{to_email}' - Subject: '{subject}' (Safe: never sent)",
        }
