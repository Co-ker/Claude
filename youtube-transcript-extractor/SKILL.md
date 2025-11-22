---
name: youtube-transcript-extractor
description: Extract YouTube video transcripts, provide English original, Korean translation, and Korean summary
triggers:
  - youtube
  - transcript
  - video
  - analyze video
  - youtube url
---

# YouTube Transcript Extractor

This skill extracts transcripts from YouTube videos and provides:
1. Original transcript in English with timestamps
2. Complete Korean translation
3. Concise Korean summary (200-300 words)

## Activation

This skill activates when you:
- Provide a YouTube URL for analysis
- Ask to extract or analyze a YouTube video transcript
- Request video content summary

## Process

When a YouTube URL is provided, I will:

1. **Extract the Transcript**
   - Use the youtube-transcript-api to fetch the video transcript
   - Prefer English captions/subtitles (manual or auto-generated)
   - Include timestamps for reference

2. **Translate to Korean**
   - Provide a complete, natural Korean translation
   - Maintain paragraph structure and flow
   - Ensure culturally appropriate expressions

3. **Create Korean Summary**
   - Identify and extract key points
   - Highlight main takeaways and insights
   - Keep summary concise (200-300 words)

## Usage Examples

**User:** "Analyze this YouTube video: https://www.youtube.com/watch?v=dQw4w9WgXcQ"

**User:** "Extract the transcript from this YouTube URL and give me a Korean summary"

**User:** "I need the transcript and Korean translation of this video: [YouTube URL]"

## Implementation

Run the extraction script and process the results:

```bash
python scripts/extract_transcript.py "<YOUTUBE_URL>"
```

Then provide:

### 📝 Original Transcript (English)

[Display the full transcript with timestamps]

### 🇰🇷 Korean Translation (한국어 번역)

[Display the complete Korean translation]

### 📋 Korean Summary (한국어 요약)

[Display the concise Korean summary with key points]

## Error Handling

If transcript extraction fails:
- Check if the video has captions/subtitles available
- Verify the URL is valid and the video is accessible
- Some videos may have disabled captions or be region-restricted

## Requirements

- Python 3.7+
- youtube-transcript-api library
- Internet connection for API access
