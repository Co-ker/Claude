---
name: youtube-discord-analyzer
description: Extract YouTube video transcripts with English original, Korean translation, summary, and send results to Discord
triggers:
  - youtube discord
  - analyze youtube
  - youtube analyzer
  - send to discord
  - youtube summary
---

# YouTube Discord Analyzer

이 스킬은 YouTube 영상의 자막을 추출하고 분석하여 디스코드 채널로 전송합니다:
1. 영어 원본 자막 (타임스탬프 포함)
2. 전체 한글 번역
3. 핵심 내용 요약 (200-300자)
4. 분석 결과를 디스코드 채널로 자동 전송

## 활성화 조건

다음과 같은 요청 시 자동 활성화됩니다:
- YouTube URL을 제공하고 분석을 요청할 때
- YouTube 영상 자막 추출 및 디스코드 전송 요청 시
- 영상 요약 및 번역 요청 시

## 처리 과정

YouTube URL이 제공되면 다음 단계를 수행합니다:

1. **자막 추출**
   - youtube-transcript-api를 사용하여 영상 자막 가져오기
   - 영어 자막 우선 (수동 또는 자동 생성)
   - 타임스탬프 포함하여 저장

2. **한글 번역**
   - 전체 자막을 자연스러운 한국어로 번역
   - 문단 구조와 흐름 유지
   - 문화적으로 적절한 표현 사용

3. **요약본 생성**
   - 핵심 내용 추출
   - 주요 포인트와 인사이트 강조
   - 200-300자 내외로 간결하게 정리

4. **디스코드 전송**
   - 분석 결과를 보기 좋게 포맷팅
   - 지정된 디스코드 채널로 전송
   - 에러 발생 시 사용자에게 알림

## 사용 예시

**사용자:** "이 YouTube 영상을 분석해서 디스코드로 보내줘: https://www.youtube.com/watch?v=dQw4w9WgXcQ"

**사용자:** "이 영상의 자막을 추출하고 한글 번역, 요약해서 디스코드 채널에 올려줘"

**사용자:** "YouTube URL 분석하고 결과를 디스코드로: [YouTube URL]"

## 구현 방법

분석 스크립트를 실행합니다:

```bash
python scripts/analyze_and_send.py "<YOUTUBE_URL>"
```

디스코드로 전송되는 형식:

### 📺 유튜브 영상 분석 결과

**🎬 영상 제목:** [영상 제목]
**🔗 링크:** [YouTube URL]

### 📝 영어 원본 (English Original)

[타임스탬프 포함 원본 자막]

### 🇰🇷 한글 번역 (Korean Translation)

[전체 한글 번역본]

### 📊 요약 (Summary)

[핵심 내용 200-300자 요약]

---

## 환경 설정

다음 환경 변수가 필요합니다 (.env 파일):

```env
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_CHANNEL_ID=your_discord_channel_id_here
GOOGLE_API_KEY=your_google_api_key_here (선택사항)
APIFY_API_KEY=your_apify_api_key_here (선택사항)
```

## 에러 처리

자막 추출 실패 시:
- 영상에 자막이 활성화되어 있는지 확인
- URL이 유효하고 영상이 접근 가능한지 확인
- 일부 영상은 자막이 비활성화되거나 지역 제한이 있을 수 있음

디스코드 전송 실패 시:
- 봇 토큰이 유효한지 확인
- 채널 ID가 정확한지 확인
- 봇이 해당 채널에 메시지 전송 권한이 있는지 확인

## 필수 요구사항

- Python 3.7+
- youtube-transcript-api 라이브러리
- discord.py 라이브러리
- python-dotenv (환경 변수 관리)
- 인터넷 연결
- 유효한 Discord 봇 토큰 및 채널 ID

## Discord 봇 설정 방법

1. Discord Developer Portal 방문: https://discord.com/developers/applications
2. 새 애플리케이션 생성
3. Bot 섹션에서 봇 추가
4. 봇 토큰 복사 (DISCORD_BOT_TOKEN)
5. OAuth2 > URL Generator에서 봇 초대 URL 생성
   - Scopes: `bot`
   - Bot Permissions: `Send Messages`, `Read Message History`
6. 생성된 URL로 서버에 봇 초대
7. 채널 ID 확인 (개발자 모드 활성화 후 채널 우클릭)
