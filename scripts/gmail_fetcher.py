from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from common import load_env_file

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def _get_service():
    creds = Credentials(
        token=None,
        refresh_token=os.getenv("GMAIL_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GMAIL_CLIENT_ID"),
        client_secret=os.getenv("GMAIL_CLIENT_SECRET"),
        scopes=SCOPES,
    )
    return build("gmail", "v1", credentials=creds)


def fetch_recent_emails(hours: int = 24) -> list[dict[str, Any]]:
    load_env_file()
    service = _get_service()

    after_ts = int((datetime.now(timezone.utc) - timedelta(hours=hours)).timestamp())
    query = f"in:inbox after:{after_ts}"

    results = service.users().messages().list(userId="me", q=query, maxResults=50).execute()
    message_refs = results.get("messages", [])

    emails = []
    for ref in message_refs:
        msg = service.users().messages().get(
            userId="me",
            id=ref["id"],
            format="metadata",
            metadataHeaders=["From", "Subject", "Date"],
        ).execute()

        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
        emails.append({
            "id": ref["id"],
            "from": headers.get("From", ""),
            "subject": headers.get("Subject", ""),
            "date": headers.get("Date", ""),
            "snippet": msg.get("snippet", ""),
        })

    return emails
