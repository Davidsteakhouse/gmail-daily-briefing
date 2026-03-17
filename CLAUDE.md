# CLAUDE.md

## 프로젝트 목적

Gmail 받은편지함에서 매일 아침 새 메일을 가져와 Gemini로 요약하고 Telegram으로 브리핑을 발송한다.

- 유튜브 협업 / 강의 제작 / 스폰서십 관련 메일만 상단에 표시
- 뉴스레터·자동메일은 스킵 카운트로 처리
- 매일 08:07 KST 자동 실행 (GitHub Actions)

## 운영 구조

- 작업 루트: `C:\Users\DanKim\Desktop\Wealth\3. ai project\1. gmail briefing`
- GitHub Actions: `.github/workflows/gmail-daily.yml`
- 실행 시각: 매일 08:07 KST (`cron: "7 23 * * *"`)
- 알림: Telegram bot message

## 파일별 역할

- `setup_oauth.py` — 최초 1회 로컬 OAuth 인증 (refresh_token 발급)
- `scripts/gmail_fetcher.py` — Gmail API로 최근 24시간 메일 수집
- `scripts/gemini_analyzer.py` — Gemini로 메일 분류 및 브리핑 생성
- `scripts/telegram_notify.py` — Telegram 발송
- `scripts/run_briefing.py` — 메인 진입점
- `scripts/common.py` — 공통 유틸 (load_env_file, request_json, KST)

## GitHub Secrets

| Secret | 설명 |
|---|---|
| `GMAIL_CLIENT_ID` | Google Cloud OAuth 클라이언트 ID |
| `GMAIL_CLIENT_SECRET` | Google Cloud OAuth 클라이언트 시크릿 |
| `GMAIL_REFRESH_TOKEN` | setup_oauth.py 실행 후 발급된 refresh token |
| `GEMINI_API_KEY` | Gemini API 키 (유튜브 대시보드와 공유 가능) |
| `TELEGRAM_BOT_TOKEN` | 텔레그램 봇 토큰 (유튜브 대시보드와 공유 가능) |
| `TELEGRAM_CHAT_ID` | 텔레그램 채팅 ID (유튜브 대시보드와 공유 가능) |

## 초기 설정 순서

1. Google Cloud Console에서 Gmail API 활성화 + OAuth 2.0 클라이언트 ID 생성
2. `credentials.json` 다운로드 후 프로젝트 루트에 저장
3. `python setup_oauth.py` 실행 → 브라우저 인증 → refresh_token 발급
4. GitHub 저장소 생성 후 Secrets 등록
5. Actions 탭에서 `Gmail Daily Briefing` 수동 실행으로 테스트

## 로컬 실행

```powershell
# .env 파일 만들고 (.env.example 참고)
python scripts/run_briefing.py
```

## 주의사항

- `credentials.json`, `token.json`, `.env`는 절대 GitHub에 올리지 않는다 (.gitignore 필수)
- Telegram BOT_TOKEN / CHAT_ID는 유튜브 대시보드 프로젝트와 동일한 값 사용 가능
