# Podcast Generator Plugin

Generate Korean podcast episodes from any source — URLs, tweets, articles, PDFs — with OpenAI TTS and auto-upload to YouTube.

## Pipeline

```
Sources → Analysis → Script → TTS (OpenAI) → MP4 → YouTube
```

## Quick Start

```bash
# Install
/plugin install podcast
```

Then just say:
- "이 글을 팟캐스트로 만들어"
- "Make a podcast from these sources"
- "Turn this into an audio episode"

## Features

- **Multi-source fusion**: Analyzes 2+ sources in parallel and synthesizes insights
- **Korean podcast script**: Conversational tone, proper number/name localization
- **OpenAI TTS**: Uses `gpt-4o-mini-tts` with `marin` voice, 1500-char chunking with retry
- **YouTube auto-upload**: OAuth browser flow, resumable upload, metadata saved
- **Partial execution**: Script-only, TTS-only, or upload-only

## Requirements

| Dependency | Purpose |
|-----------|---------|
| ffmpeg | Audio merging + MP4 conversion |
| OpenAI API key | TTS generation (`OPENAI_API_KEY` env var) |
| Google OAuth client secret | YouTube upload |
| Python 3.10+ | All scripts (stdlib only, no pip) |

## Setup

### OpenAI TTS
Set `OPENAI_API_KEY` environment variable, or provide when prompted.

### YouTube Upload
1. Create a Google Cloud project with YouTube Data API v3 enabled
2. Download OAuth client secret JSON
3. Place in `~/Downloads/client_secret_*.json`
4. First upload will open browser for authentication

## License

MIT
