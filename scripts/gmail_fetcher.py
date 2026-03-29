from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from typing import Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from common import load_env_file

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def _exchange_refresh_token(client_id: str, client_secret: str, refresh_token: str) -> str:
    data = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }).encode()
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data, method="POST")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())["access_token"]


def _get_service():
    client_id = os.getenv("GMAIL_CLIENT_ID")
    client_secret = os.getenv("GMAIL_CLIENT_SECRET")
    refresh_token = os.getenv("GMAIL_REFRESH_TOKEN")
    access_token = _exchange_refresh_token(client_id, client_secret, refresh_token)
    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
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
