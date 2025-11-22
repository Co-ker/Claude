#!/usr/bin/env python3
"""
YouTube Transcript Extractor
Extracts transcripts from YouTube videos with error handling
"""

import sys
import re
import json
from typing import Optional, List, Dict
from urllib.parse import urlparse, parse_qs


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


def format_transcript(transcript: List[Dict], include_timestamps: bool = True) -> str:
    """Format transcript with or without timestamps"""
    lines = []

    for entry in transcript:
        text = entry['text'].strip()
        if include_timestamps:
            timestamp = format_timestamp(entry['start'])
            lines.append(f"[{timestamp}] {text}")
        else:
            lines.append(text)

    return '\n'.join(lines)


def get_plain_text(transcript: List[Dict]) -> str:
    """Get plain text without timestamps for translation"""
    return ' '.join(entry['text'].strip() for entry in transcript)


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_transcript.py <YOUTUBE_URL>", file=sys.stderr)
        sys.exit(1)

    video_url = sys.argv[1]

    # Extract transcript
    result = extract_transcript(video_url)

    # Output as JSON for easy parsing
    print(json.dumps(result, indent=2, ensure_ascii=False))

    if not result['success']:
        sys.exit(1)


if __name__ == '__main__':
    main()
