"""
Gmail OAuth 최초 인증 스크립트 (로컬 1회 실행용)

실행 방법:
    python setup_oauth.py

완료 후 token.json에서 refresh_token 값을 복사해
GitHub Secrets에 GMAIL_REFRESH_TOKEN으로 등록하세요.
"""
from __future__ import annotations

import json
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CREDENTIALS_FILE = Path("credentials.json")
TOKEN_FILE = Path("token.json")


def main() -> None:
    if not CREDENTIALS_FILE.exists():
        print("credentials.json 파일이 없습니다.")
        print("Google Cloud Console에서 OAuth 2.0 클라이언트 ID를 다운로드해서")
        print("이 폴더에 credentials.json으로 저장하세요.")
        return

    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
    creds = flow.run_local_server(port=0)

    token_data = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": list(creds.scopes),
    }
    TOKEN_FILE.write_text(json.dumps(token_data, indent=2), encoding="utf-8")

    print("\n인증 완료!")
    print(f"refresh_token: {creds.refresh_token}")
    print("\nGitHub Secrets에 다음 값들을 등록하세요:")
    print(f"  GMAIL_CLIENT_ID     = {creds.client_id}")
    print(f"  GMAIL_CLIENT_SECRET = {creds.client_secret}")
    print(f"  GMAIL_REFRESH_TOKEN = {creds.refresh_token}")


if __name__ == "__main__":
    main()
