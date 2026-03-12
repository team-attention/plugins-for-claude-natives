---
name: podcast
description: "Generate Korean podcast episodes from any source (URLs, tweets, articles, PDFs) — analyzes content, writes a script, generates audio via OpenAI TTS, converts to MP4, and auto-uploads to YouTube. Use this skill whenever the user says 'make a podcast', 'convert to podcast', 'podcast', 'create an episode', 'turn this into audio', 'YouTube podcast', 'turn this article into a podcast', 'publish as audio', or provides sources and wants them transformed into a listenable format. Supports partial execution: script-only, TTS-only, or upload-only."
---

# Podcast Generator

Analyze sources, generate a Korean podcast script, produce audio via OpenAI TTS, and auto-upload to YouTube.

## Pipeline

```
[Source Collection] → [Analysis/Fusion] → [Script Writing] → [TTS Generation] → [MP4 Conversion] → [YouTube Upload]
```

## Step 1: Source Collection & Analysis

Collect and analyze user-provided sources. Processing by type:

- **URL/Article**: WebFetch or subagent for full text
- **Tweet/X post**: Use WebFetch with `api.fxtwitter.com` (replace domain in X/Twitter URL)
- **PDF**: Read tool directly
- **GitHub repo**: Clone and analyze structure (use subagent)
- **Conversation context**: Reuse content already analyzed in current session

When 2+ sources are provided, **always spawn parallel subagents** for each.

## Step 2: Script Writing

### Structure (8-12 min, 3000-5000 chars)

```markdown
# [Episode Title]

> [Duration] podcast script | [Date]
> Sources: [source list]

---

## Opening (1 min)
- Hook: one sentence on why this topic matters
- Introduce sources
- Lead with conclusion (state core message upfront)

## Body Part 1 (3 min)
- Deep analysis of first source/perspective

## Body Part 2 (3 min)
- Deep analysis of second source/perspective

## Fusion/Intersection (3 min)
- Emergent insights from combining sources
- Patterns, commonalities, contrasts
- Generalizable implications

## Closing (30 sec)
- One-sentence summary of core message
- Sign-off
```

### Script Writing Principles

- **Write as you speak**: conversational Korean ("~입니다", "~거죠", "~인데요")
- **Numbers in Korean**: "267K" → "이십육만", "$75,000" → "칠만오천 달러"
- **English names in Korean pronunciation**: "Garry Tan" → "개리 탄"
- **No tables or code blocks**: TTS cannot read them. Convert table content to sentences
- **Shift tone for quotes**: "개리 탄 본인이 이렇게 말합니다." to create distinction
- **Short sentences**: keep each sentence under 50 characters

### File Layout

```
<output-dir>/
├── script.md       ← Script
├── episode.mp3     ← Audio
├── episode.mp4     ← Video (for YouTube)
└── metadata.json   ← Title, description, tags, YouTube URL
```

The output directory can be any user-specified path. A sensible default is `podcast/YYYY-MM-DD-[slug]/` relative to the current working directory.

## Step 3: TTS Generation

Convert script to audio using `scripts/generate_tts.py`:

```bash
python3 <plugin-path>/skills/podcast/scripts/generate_tts.py \
  --input <script.md path> \
  --output <episode.mp3 path> \
  --api-key <OpenAI API key>
```

Replace `<plugin-path>` with the actual path where this plugin is installed (use `${CLAUDE_PLUGIN_ROOT}` if available, or the resolved plugin installation path).

### OpenAI API Key

Check `OPENAI_API_KEY` environment variable first. If not set, ask the user.

### TTS Settings

| Setting | Value | Note |
|---------|-------|------|
| Model | `gpt-4o-mini-tts` | Latest model with instructions support |
| Voice | `marin` | Best for Korean. `cedar` as alternative |
| Chunk size | 1500 chars | 2000 token limit, Korean ~1.5 char/token |
| Instructions | Auto-generated per script | See default below |

Default TTS instructions:
> "따뜻하고 친근한 한국어 팟캐스트 호스트. 명확한 발음으로 또박또박 읽되, 자연스러운 억양과 적절한 감정을 담아서. 중요한 포인트에서는 약간 힘을 주고, 인용구에서는 톤을 살짝 바꿔서 구분감을 준다. 전체적으로 지적이면서도 편안한 분위기."

If the user specifies a tone, customize via `--instructions`.

## Step 4: MP4 Conversion

Convert MP3 to MP4 with a static title card:

```bash
python3 <plugin-path>/skills/podcast/scripts/convert_mp4.py \
  --input <episode.mp3 path> \
  --output <episode.mp4 path> \
  --title "Episode Title" \
  --subtitle "Subtitle"
```

Generates a 1920x1080 video with dark background (#1a1a2e) and Korean title/subtitle overlay.

## Step 5: YouTube Upload

```bash
python3 <plugin-path>/skills/podcast/scripts/upload_youtube.py \
  --video <episode.mp4 path> \
  --title "Episode Title" \
  --description "Description" \
  --privacy unlisted
```

### OAuth Setup

- Google OAuth client secret: auto-discovers `~/Downloads/client_secret_*.json` or `~/.config/google/client_secret_*.json`
- Token: stored alongside the video file by default (override with `--token-path`)
- First run requires browser-based Google authentication
- Ask user which YouTube account to use if multiple are available
- Never copy scripts to the episode directory. Always run from the plugin's original path

### Upload Defaults

- Privacy: `unlisted` (unless user specifies otherwise)
- Category: People & Blogs (22)
- Language: ko

## Step 6: Completion Report

After upload, report to user:

```
Done!
- Script: <path>/script.md
- Audio: <path>/episode.mp3
- Video: <path>/episode.mp4
- YouTube: https://youtu.be/VIDEO_ID (unlisted)
```

Play `episode.mp3` with `afplay` so the user can listen immediately.

## Partial Execution

Users may request only part of the pipeline:

- "Just write the script" → Steps 1-2 only
- "Generate TTS from this script" → Step 3 only
- "Upload to YouTube" → Step 5 only (requires existing MP4)
- "Make it public" → Update YouTube privacy via API

## Requirements

- **ffmpeg**: required for audio merging and MP4 conversion. On macOS, `homebrew-ffmpeg/ffmpeg` tap may be needed for full codec support
- **OpenAI API key**: for TTS generation (`OPENAI_API_KEY` env var or provided by user)
- **Google OAuth client secret**: for YouTube upload (download from Google Cloud Console)
- **macOS font**: uses `/System/Library/Fonts/AppleSDGothicNeo.ttc` for Korean text overlay. On other platforms, adjust `FONT_PATH` in `convert_mp4.py`
- **Python 3.10+**: all scripts use standard library only (no pip install needed)
