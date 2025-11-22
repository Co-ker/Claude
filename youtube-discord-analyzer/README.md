# 📺 YouTube Discord Analyzer

YouTube 영상의 자막을 추출하고 분석하여 디스코드 채널로 자동 전송하는 스킬입니다.

## 🎯 주요 기능

1. **자막 추출**: YouTube 영상에서 영어 자막 자동 추출
2. **타임스탬프**: 원본 자막에 타임스탬프 포함
3. **한글 번역**: 전체 내용을 한국어로 번역 (API 설정 필요)
4. **핵심 요약**: 200-300자 분량의 한글 요약본 생성 (API 설정 필요)
5. **디스코드 전송**: 분석 결과를 지정된 디스코드 채널로 자동 전송

## 📋 필수 요구사항

- Python 3.7 이상
- Discord 봇 토큰 및 채널 ID
- 인터넷 연결

## 🚀 설치 방법

### 1. 필수 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env.example` 파일을 `.env`로 복사하고 필요한 값을 입력하세요:

```bash
cp .env.example .env
```

`.env` 파일 내용:

```env
# 필수 항목
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_CHANNEL_ID=your_discord_channel_id_here

# 선택 항목
GOOGLE_API_KEY=your_google_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

## 🤖 Discord 봇 설정

### 1. Discord 봇 생성

1. [Discord Developer Portal](https://discord.com/developers/applications) 접속
2. "New Application" 클릭하여 새 애플리케이션 생성
3. 애플리케이션 이름 입력 (예: YouTube Analyzer)

### 2. 봇 추가 및 토큰 받기

1. 왼쪽 메뉴에서 "Bot" 선택
2. "Add Bot" 클릭
3. "Reset Token" 클릭하여 봇 토큰 생성
4. 토큰 복사 → `.env` 파일의 `DISCORD_BOT_TOKEN`에 붙여넣기

### 3. 봇 권한 설정

"Bot" 페이지에서 다음 권한 활성화:
- ✅ MESSAGE CONTENT INTENT
- ✅ Send Messages
- ✅ Read Message History

### 4. 봇 초대 URL 생성

1. 왼쪽 메뉴에서 "OAuth2" → "URL Generator" 선택
2. **Scopes** 섹션에서:
   - ✅ `bot` 체크
3. **Bot Permissions** 섹션에서:
   - ✅ Send Messages
   - ✅ Read Message History
   - ✅ Embed Links
4. 하단에 생성된 URL 복사

### 5. 서버에 봇 초대

1. 생성된 URL을 브라우저에 붙여넣기
2. 봇을 추가할 디스코드 서버 선택
3. 권한 확인 후 "인증" 클릭

### 6. 채널 ID 확인

1. Discord 앱 설정 → "고급" → "개발자 모드" 활성화
2. 원하는 채널에서 우클릭 → "채널 ID 복사"
3. `.env` 파일의 `DISCORD_CHANNEL_ID`에 붙여넣기

## 💻 사용 방법

### 기본 사용법

```bash
cd youtube-discord-analyzer
python scripts/analyze_and_send.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 예제

```bash
python scripts/analyze_and_send.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### 출력 예시

스크립트 실행 시 콘솔 출력:
```
📥 Extracting transcript from: https://www.youtube.com/watch?v=dQw4w9WgXcQ
✅ Transcript extracted successfully! (Video ID: dQw4w9WgXcQ)
📝 Fetching video title...
📄 Formatting transcript...
🇰🇷 Generating Korean translation...
📊 Generating Korean summary...
📤 Sending results to Discord...
✅ Successfully sent analysis to Discord channel 123456789
✅ Analysis completed and sent to Discord successfully!
```

디스코드 채널에 전송되는 형식:
```
📺 유튜브 영상 분석 결과

🎬 영상 제목: Example Video Title
🔗 링크: https://www.youtube.com/watch?v=dQw4w9WgXcQ

📝 영어 원본 (English Original)
[00:00] First line of transcript
[00:05] Second line of transcript
...

🇰🇷 한글 번역 (Korean Translation)
자막의 전체 한글 번역...

📊 요약 (Summary)
영상의 핵심 내용 요약...
```

## 🔧 고급 설정

### Google YouTube Data API 설정 (선택사항)

영상 제목을 자동으로 가져오려면:

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성
3. "YouTube Data API v3" 활성화
4. API 키 생성
5. `.env` 파일의 `GOOGLE_API_KEY`에 추가

### 자동 번역/요약 기능 (향후 개선 예정)

현재는 번역과 요약 기능이 플레이스홀더로 되어 있습니다. 실제 번역/요약을 사용하려면:

1. Claude API 또는 다른 번역 API 통합 필요
2. `scripts/analyze_and_send.py`의 다음 함수 수정:
   - `generate_korean_translation()`
   - `generate_korean_summary()`

## 📁 프로젝트 구조

```
youtube-discord-analyzer/
├── SKILL.md              # 스킬 메타데이터 및 설명
├── README.md             # 이 파일
├── requirements.txt      # Python 패키지 목록
├── .env.example          # 환경 변수 템플릿
└── scripts/
    └── analyze_and_send.py  # 메인 실행 스크립트
```

## 🐛 문제 해결

### 자막 추출 실패

**문제**: "No transcript found" 에러
- **해결**: 해당 영상에 자막이 있는지 확인하세요. 일부 영상은 자막이 없거나 비활성화되어 있습니다.

**문제**: "Video is unavailable" 에러
- **해결**: 영상이 비공개, 삭제되었거나 지역 제한이 있는지 확인하세요.

### Discord 전송 실패

**문제**: "Could not find channel" 에러
- **해결**:
  1. 채널 ID가 정확한지 확인
  2. 봇이 해당 서버에 초대되었는지 확인
  3. 봇이 해당 채널을 볼 수 있는 권한이 있는지 확인

**문제**: "403 Forbidden" 에러
- **해결**: 봇에게 메시지 전송 권한이 있는지 확인하세요.

**문제**: "Invalid token" 에러
- **해결**: Discord Developer Portal에서 봇 토큰을 다시 확인하세요.

## 🔐 보안 주의사항

- ⚠️ `.env` 파일을 절대 Git에 커밋하지 마세요!
- ⚠️ 봇 토큰을 공개하지 마세요!
- ⚠️ `.gitignore`에 `.env`가 포함되어 있는지 확인하세요!

## 📝 라이선스

이 프로젝트는 자유롭게 사용하실 수 있습니다.

## 🤝 기여

개선 사항이나 버그 리포트는 언제든 환영합니다!

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. Python 버전이 3.7 이상인지 확인
2. 모든 패키지가 올바르게 설치되었는지 확인
3. `.env` 파일의 모든 필수 값이 입력되었는지 확인
4. Discord 봇이 올바르게 설정되었는지 확인

---

Made with ❤️ for YouTube content analysis
