from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

from common import load_env_file, request_json, KST

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"

DAY_KO = {"Mon": "월", "Tue": "화", "Wed": "수", "Thu": "목", "Fri": "금", "Sat": "토", "Sun": "일"}


def _kst_date_str() -> str:
    now = datetime.now(KST)
    date_str = now.strftime("%m/%d (%a)")
    for en, ko in DAY_KO.items():
        date_str = date_str.replace(en, ko)
    return date_str


def analyze_emails(emails: list[dict[str, Any]]) -> str:
    load_env_file()
    date_str = _kst_date_str()

    if not emails:
        return f"📬 메일 브리핑 | {date_str}\n\n받은 메일이 없습니다."

    email_list_text = "\n\n".join(
        f"[{i+1}] From: {e['from']}\nSubject: {e['subject']}\nSnippet: {e['snippet']}"
        for i, e in enumerate(emails)
    )

    prompt = f"""다음은 오늘 받은 이메일 목록입니다.

{email_list_text}

당신은 AI 유튜브 크리에이터의 비서입니다.
아래 기준으로 분류하고 텔레그램 브리핑 메시지를 작성해주세요.

[챙길 메일 기준]
- 유튜브 협업 제안
- 강의 제작 관련 (클래스101, 인프런 등)
- 스폰서십 / 브랜드 협업 문의
- 콘텐츠 관련 중요 연락

[무시할 메일]
- 뉴스레터, 자동 발송, 광고성 메일

[출력 형식 - 정확히 지켜주세요]
📬 메일 브리핑 | {date_str}

🎯 챙길 메일 N건
━━━━━━━━━━━━━━━
1. 발신자명 (소속/채널명)
   제목 — 한줄 핵심 요약
   👉 답장 필요

(챙길 메일이 없으면 "🎯 챙길 메일 없음" 으로 표시)
━━━━━━━━━━━━━━━
📭 뉴스레터/자동메일 N건 스킵

규칙:
- 챙길 메일만 번호 매겨 나열, 나머지는 스킵 카운트에 포함
- 👉 액션은 "답장 필요" / "확인 필요" / "검토" 중 하나만 사용
- 한국어로 작성"""

    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    response = request_json(
        f"{GEMINI_API_BASE}/models/{model}:generateContent",
        method="POST",
        params={"key": api_key},
        payload={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.3, "maxOutputTokens": 1024},
        },
    )
    return response["candidates"][0]["content"]["parts"][0]["text"].strip()
