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


def fetch_unanswered_emails(days: int = 7) -> list[dict[str, Any]]:
    """최근 N일 받은편지함에서 내가 아직 답장 안 한 메일만 반환."""
    load_env_file()
    service = _get_service()

    profile = service.users().getProfile(userId="me").execute()
    user_email = profile["emailAddress"].lower()

    after_ts = int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp())
    query = f"in:inbox after:{after_ts}"

    results = service.users().threads().list(userId="me", q=query, maxResults=50).execute()
    thread_refs = results.get("threads", [])

    emails = []
    for ref in thread_refs:
        thread = service.users().threads().get(
            userId="me",
            id=ref["id"],
            format="metadata",
            metadataHeaders=["From", "Subject", "Date"],
        ).execute()

        messages = thread.get("messages", [])

        # 스레드 내 내가 보낸 메일이 있으면 답장 완료 → 스킵
        replied = any(
            user_email in next(
                (h["value"] for h in msg.get("payload", {}).get("headers", []) if h["name"] == "From"),
                ""
            ).lower()
            for msg in messages
        )
        if replied:
            continue

        # 첫 번째 메시지(원본) 기준으로 정보 추출
        first = messages[0]
        headers = {h["name"]: h["value"] for h in first.get("payload", {}).get("headers", [])}

        emails.append({
            "id": first["id"],
            "from": headers.get("From", ""),
            "subject": headers.get("Subject", ""),
            "date": headers.get("Date", ""),
            "snippet": first.get("snippet", "")[:200],
        })

    return emails
