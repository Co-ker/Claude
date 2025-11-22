#!/usr/bin/env python3
"""
YouTube Discord Analyzer
Extracts YouTube video transcripts, translates to Korean, summarizes, and sends to Discord
"""

import sys
import os
import re
import json
import asyncio
from typing import Optional, List, Dict
from urllib.parse import urlparse, parse_qs
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    # Load .env from current directory or parent directory
    env_path = Path('.env')
    if not env_path.exists():
        env_path = Path('..') / '.env'
    if not env_path.exists():
        env_path = Path('../..') / '.env'
    load_dotenv(env_path)
except ImportError:
    print("Warning: python-dotenv not installed. Skipping .env file loading.", file=sys.stderr)


def extract_video_id(url: str) -> Optional[str]:
    """
    Extract YouTube video ID from various URL formats

    Supports:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    """
    # Pattern 1: youtube.com/watch?v=VIDEO_ID
    if 'youtube.com/watch' in url:
        parsed = urlparse(url)
        video_id = parse_qs(parsed.query).get('v')
        if video_id:
            return video_id[0]

    # Pattern 2: youtu.be/VIDEO_ID
    if 'youtu.be/' in url:
        parsed = urlparse(url)
        return parsed.path.lstrip('/')

    # Pattern 3: youtube.com/embed/VIDEO_ID
    if 'youtube.com/embed/' in url:
        parsed = urlparse(url)
        return parsed.path.split('/embed/')[-1]

    # If it's just a video ID
    if re.match(r'^[A-Za-z0-9_-]{11}$', url):
        return url

    return None


def format_timestamp(seconds: float) -> str:
    """Convert seconds to MM:SS or HH:MM:SS format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def extract_transcript(video_url: str) -> Dict:
    """
    Extract transcript from YouTube video

    Returns a dictionary with:
    - success: bool
    - video_id: str
    - transcript: List[Dict] (if successful)
    - error: str (if failed)
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        from youtube_transcript_api._errors import (
            TranscriptsDisabled,
            NoTranscriptFound,
            VideoUnavailable
        )
    except ImportError:
        return {
            'success': False,
            'error': 'youtube-transcript-api is not installed. Please install it with: pip install youtube-transcript-api'
        }

    # Extract video ID
    video_id = extract_video_id(video_url)
    if not video_id:
        return {
            'success': False,
            'error': f'Could not extract video ID from URL: {video_url}'
        }

    try:
        # Try to get English transcript first
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        except NoTranscriptFound:
            # If English not available, get any available transcript
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = transcript_list.find_transcript(['en']).fetch()

        return {
            'success': True,
            'video_id': video_id,
            'transcript': transcript
        }

    except TranscriptsDisabled:
        return {
            'success': False,
            'video_id': video_id,
            'error': 'Transcripts are disabled for this video'
        }
    except NoTranscriptFound:
        return {
            'success': False,
            'video_id': video_id,
            'error': 'No transcript found for this video (no captions available)'
        }
    except VideoUnavailable:
        return {
            'success': False,
            'video_id': video_id,
            'error': 'Video is unavailable (may be private, deleted, or region-restricted)'
        }
    except Exception as e:
        return {
            'success': False,
            'video_id': video_id,
            'error': f'Unexpected error: {str(e)}'
        }


def format_transcript_with_timestamps(transcript: List[Dict]) -> str:
    """Format transcript with timestamps"""
    lines = []
    for entry in transcript:
        text = entry['text'].strip()
        timestamp = format_timestamp(entry['start'])
        lines.append(f"[{timestamp}] {text}")
    return '\n'.join(lines)


def get_plain_text(transcript: List[Dict]) -> str:
    """Get plain text without timestamps"""
    return ' '.join(entry['text'].strip() for entry in transcript)


def get_video_title(video_id: str) -> str:
    """
    Get video title using YouTube Data API
    Falls back to video ID if API is not configured
    """
    api_key = os.getenv('GOOGLE_API_KEY')

    if not api_key:
        return f"Video {video_id}"

    try:
        from googleapiclient.discovery import build
        youtube = build('youtube', 'v3', developerKey=api_key)

        request = youtube.videos().list(
            part='snippet',
            id=video_id
        )
        response = request.execute()

        if response['items']:
            return response['items'][0]['snippet']['title']
        else:
            return f"Video {video_id}"
    except Exception as e:
        print(f"Warning: Could not fetch video title: {e}", file=sys.stderr)
        return f"Video {video_id}"


async def send_to_discord(
    video_url: str,
    video_title: str,
    original_text: str,
    korean_translation: str,
    korean_summary: str
) -> bool:
    """
    Send analysis results to Discord channel

    Returns True if successful, False otherwise
    """
    try:
        import discord
    except ImportError:
        print("Error: discord.py is not installed. Please install it with: pip install discord.py", file=sys.stderr)
        return False

    token = os.getenv('DISCORD_BOT_TOKEN')
    channel_id = os.getenv('DISCORD_CHANNEL_ID')

    if not token:
        print("Error: DISCORD_BOT_TOKEN not found in environment variables", file=sys.stderr)
        return False

    if not channel_id:
        print("Error: DISCORD_CHANNEL_ID not found in environment variables", file=sys.stderr)
        return False

    try:
        channel_id = int(channel_id)
    except ValueError:
        print(f"Error: DISCORD_CHANNEL_ID must be a number, got: {channel_id}", file=sys.stderr)
        return False

    # Create Discord client
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    success = False

    @client.event
    async def on_ready():
        nonlocal success
        try:
            channel = client.get_channel(channel_id)
            if not channel:
                print(f"Error: Could not find channel with ID: {channel_id}", file=sys.stderr)
                await client.close()
                return

            # Split message into chunks if needed (Discord has 2000 char limit)
            header = f"""📺 **유튜브 영상 분석 결과**

🎬 **영상 제목:** {video_title}
🔗 **링크:** {video_url}

"""

            # Send header
            await channel.send(header)

            # Send original transcript
            original_chunks = split_message(f"📝 **영어 원본 (English Original)**\n```\n{original_text}\n```")
            for chunk in original_chunks:
                await channel.send(chunk)

            # Send Korean translation
            translation_chunks = split_message(f"🇰🇷 **한글 번역 (Korean Translation)**\n\n{korean_translation}")
            for chunk in translation_chunks:
                await channel.send(chunk)

            # Send summary
            summary_msg = f"📊 **요약 (Summary)**\n\n{korean_summary}"
            await channel.send(summary_msg)

            print(f"✅ Successfully sent analysis to Discord channel {channel_id}")
            success = True

        except Exception as e:
            print(f"Error sending message to Discord: {e}", file=sys.stderr)

        await client.close()

    try:
        await client.start(token)
    except Exception as e:
        print(f"Error connecting to Discord: {e}", file=sys.stderr)
        return False

    return success


def split_message(text: str, max_length: int = 1900) -> List[str]:
    """
    Split message into chunks that fit Discord's character limit
    Keeps code blocks intact
    """
    if len(text) <= max_length:
        return [text]

    chunks = []
    current_chunk = ""
    in_code_block = False

    lines = text.split('\n')

    for line in lines:
        # Check if this line starts or ends a code block
        if line.strip().startswith('```'):
            in_code_block = not in_code_block

        # If adding this line exceeds limit and we're not in a code block
        if len(current_chunk) + len(line) + 1 > max_length and not in_code_block:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = line + '\n'
        else:
            current_chunk += line + '\n'

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def generate_korean_translation(text: str) -> str:
    """
    Generate Korean translation of the text using OpenAI API
    """
    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        return """[번역 실패: OPENAI_API_KEY가 설정되지 않았습니다]

.env 파일에 다음을 추가하세요:
OPENAI_API_KEY=your_openai_api_key_here

OpenAI API 키는 https://platform.openai.com/api-keys 에서 발급받을 수 있습니다."""

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # 저렴하고 빠른 모델
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional translator. Translate the following English text to natural, fluent Korean. Maintain the original meaning and tone."
                },
                {
                    "role": "user",
                    "content": f"Translate this English text to Korean:\n\n{text}"
                }
            ],
            temperature=0.3,
            max_tokens=4000
        )

        translation = response.choices[0].message.content.strip()
        return translation

    except ImportError:
        return "[번역 실패: openai 라이브러리가 설치되지 않았습니다. 'pip install openai'를 실행하세요]"
    except Exception as e:
        return f"[번역 중 오류 발생: {str(e)}]"


def generate_korean_summary(text: str) -> str:
    """
    Generate a Korean summary of the text (200-300 characters) using OpenAI API
    """
    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        return """[요약 실패: OPENAI_API_KEY가 설정되지 않았습니다]

.env 파일에 다음을 추가하세요:
OPENAI_API_KEY=your_openai_api_key_here

OpenAI API 키는 https://platform.openai.com/api-keys 에서 발급받을 수 있습니다."""

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # 저렴하고 빠른 모델
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert summarizer. Create concise, informative summaries in Korean."
                },
                {
                    "role": "user",
                    "content": f"""다음 영어 텍스트를 읽고 핵심 내용을 한국어로 요약해주세요.

요구사항:
- 200-300자 정도의 간결한 요약
- 주요 포인트와 핵심 메시지 포함
- 한국어로 작성
- 불릿 포인트나 번호 목록 사용 가능

텍스트:
{text}"""
                }
            ],
            temperature=0.5,
            max_tokens=1000
        )

        summary = response.choices[0].message.content.strip()
        return summary

    except ImportError:
        return "[요약 실패: openai 라이브러리가 설치되지 않았습니다. 'pip install openai'를 실행하세요]"
    except Exception as e:
        return f"[요약 중 오류 발생: {str(e)}]"


async def main_async():
    """Main async function"""
    if len(sys.argv) < 2:
        print("Usage: python analyze_and_send.py <YOUTUBE_URL>", file=sys.stderr)
        sys.exit(1)

    video_url = sys.argv[1]

    print(f"📥 Extracting transcript from: {video_url}")

    # Extract transcript
    result = extract_transcript(video_url)

    if not result['success']:
        print(f"❌ Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    video_id = result['video_id']
    transcript = result['transcript']

    print(f"✅ Transcript extracted successfully! (Video ID: {video_id})")

    # Get video title
    print("📝 Fetching video title...")
    video_title = get_video_title(video_id)

    # Format transcript
    print("📄 Formatting transcript...")
    original_with_timestamps = format_transcript_with_timestamps(transcript)
    plain_text = get_plain_text(transcript)

    # Generate translation and summary
    print("🇰🇷 Generating Korean translation...")
    korean_translation = generate_korean_translation(plain_text)

    print("📊 Generating Korean summary...")
    korean_summary = generate_korean_summary(plain_text)

    # Print results to console
    print("\n" + "="*60)
    print("ANALYSIS RESULTS")
    print("="*60)
    print(f"\n🎬 Title: {video_title}")
    print(f"🔗 URL: {video_url}")
    print(f"\n📝 Original Transcript Length: {len(original_with_timestamps)} characters")
    print(f"📝 Plain Text Length: {len(plain_text)} characters")
    print("="*60 + "\n")

    # Send to Discord
    print("📤 Sending results to Discord...")
    success = await send_to_discord(
        video_url=video_url,
        video_title=video_title,
        original_text=original_with_timestamps,
        korean_translation=korean_translation,
        korean_summary=korean_summary
    )

    if success:
        print("\n✅ Analysis completed and sent to Discord successfully!")
        return 0
    else:
        print("\n❌ Failed to send results to Discord", file=sys.stderr)
        return 1


def main():
    """Main function"""
    return asyncio.run(main_async())


if __name__ == '__main__':
    sys.exit(main())
