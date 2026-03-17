from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from common import load_env_file
from gmail_fetcher import fetch_unanswered_emails
from gemini_analyzer import analyze_emails
from telegram_notify import send_message


def main() -> None:
    load_env_file()

    print("메일 가져오는 중...")
    emails = fetch_unanswered_emails(days=7)
    print(f"총 {len(emails)}건 수집")

    print("Gemini 분석 중...")
    briefing = analyze_emails(emails)
    print("--- 브리핑 미리보기 ---")
    print(briefing)
    print("----------------------")

    print("텔레그램 발송 중...")
    send_message(briefing)
    print("완료!")


if __name__ == "__main__":
    main()
