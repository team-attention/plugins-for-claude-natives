#!/usr/bin/env python3
"""OpenAI gpt-4o-mini-tts로 팟캐스트 음성 생성 — 청크 분할 + ffmpeg 병합"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

DEFAULT_MODEL = "gpt-4o-mini-tts"
DEFAULT_VOICE = "marin"
DEFAULT_INSTRUCTIONS = (
    "따뜻하고 친근한 한국어 팟캐스트 호스트. "
    "명확한 발음으로 또박또박 읽되, 자연스러운 억양과 적절한 감정을 담아서. "
    "중요한 포인트에서는 약간 힘을 주고, 인용구에서는 톤을 살짝 바꿔서 구분감을 준다. "
    "전체적으로 지적이면서도 편안한 분위기."
)
MAX_CHARS = 1500  # gpt-4o-mini-tts: 2000 token limit, 한국어 ~1.5 char/token


def extract_speech_text(md_path):
    """마크다운에서 실제 대사만 추출 (헤더, 메타데이터, 테이블, 코드블록 제거)"""
    with open(md_path, "r") as f:
        text = f.read()

    lines = text.split("\n")
    speech_lines = []
    skip = False
    for line in lines:
        if line.startswith("# ") and speech_lines == []:
            continue
        if line.startswith(">"):
            continue
        if line.startswith("---"):
            continue
        if line.startswith("## "):
            speech_lines.append("")
            continue
        if line.startswith("```"):
            skip = not skip
            continue
        if line.startswith("|"):
            continue
        if skip:
            continue
        clean = line.strip()
        clean = re.sub(r'\*\*(.+?)\*\*', r'\1', clean)
        clean = re.sub(r'\*(.+?)\*', r'\1', clean)
        clean = re.sub(r'`(.+?)`', r'\1', clean)
        clean = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', clean)
        clean = re.sub(r'^[-*]\s+', '', clean)  # 불릿 마커 제거
        if clean:
            speech_lines.append(clean)

    return "\n".join(speech_lines)


def split_paragraph_by_sentences(para, max_chars=MAX_CHARS):
    """단일 문단이 max_chars를 초과할 때 문장 단위로 분할"""
    sentences = re.split(r'(?<=[.!?。])\s+', para)
    chunks = []
    current = ""
    for sent in sentences:
        if len(current) + len(sent) + 1 > max_chars:
            if current:
                chunks.append(current.strip())
            if len(sent) > max_chars:
                for i in range(0, len(sent), max_chars):
                    chunks.append(sent[i:i + max_chars])
                current = ""
            else:
                current = sent
        else:
            current = current + " " + sent if current else sent
    if current.strip():
        chunks.append(current.strip())
    return chunks


def split_into_chunks(text, max_chars=MAX_CHARS):
    """문단 단위로 청크 분할 (초과 문단은 문장 단위로 재분할)"""
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(para) > max_chars:
            if current:
                chunks.append(current.strip())
                current = ""
            chunks.extend(split_paragraph_by_sentences(para, max_chars))
            continue
        if len(current) + len(para) + 2 > max_chars:
            if current:
                chunks.append(current.strip())
            current = para
        else:
            current = current + "\n\n" + para if current else para

    if current.strip():
        chunks.append(current.strip())

    return chunks


def generate_tts_chunk(text, output_path, api_key, model, voice, instructions,
                       max_retries=3):
    """OpenAI TTS API 단일 청크 호출 (재시도 + 지수 백오프)"""
    payload = {
        "model": model,
        "input": text,
        "voice": voice,
        "response_format": "mp3",
    }
    if instructions:
        payload["instructions"] = instructions

    data = json.dumps(payload).encode("utf-8")

    for attempt in range(max_retries):
        req = urllib.request.Request(
            "https://api.openai.com/v1/audio/speech",
            data=data,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                with open(output_path, "wb") as f:
                    f.write(resp.read())
            return
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            if e.code == 429 or e.code >= 500:
                wait = 2 ** attempt
                print(f"    Retry {attempt+1}/{max_retries} (waiting {wait}s)...",
                      file=sys.stderr)
                time.sleep(wait)
                continue
            print(f"    API Error {e.code}: {body}", file=sys.stderr)
            raise
        except (urllib.error.URLError, TimeoutError):
            if attempt < max_retries - 1:
                wait = 2 ** attempt
                print(f"    Network error, retry {attempt+1}/{max_retries} (waiting {wait}s)...",
                      file=sys.stderr)
                time.sleep(wait)
                continue
            raise

    raise RuntimeError(f"TTS API failed after {max_retries} attempts")


def merge_audio(chunk_files, output_path):
    """ffmpeg concat으로 청크 병합"""
    if len(chunk_files) == 1:
        os.rename(chunk_files[0], output_path)
        return

    output_dir = os.path.dirname(output_path)
    list_file = os.path.join(output_dir, "_chunks.txt")
    with open(list_file, "w") as f:
        for cf in chunk_files:
            f.write(f"file '{cf}'\n")

    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
         "-i", list_file, "-c", "copy", output_path],
        check=True, capture_output=True,
    )

    os.remove(list_file)
    for cf in chunk_files:
        os.remove(cf)


def get_duration(path):
    """ffprobe로 오디오 길이 반환 (초)"""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True,
    )
    return float(result.stdout.strip())


def main():
    parser = argparse.ArgumentParser(description="Podcast TTS Generation")
    parser.add_argument("--input", required=True, help="Script markdown path")
    parser.add_argument("--output", required=True, help="Output MP3 path")
    parser.add_argument("--api-key", default=os.environ.get("OPENAI_API_KEY", ""), help="OpenAI API key")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--voice", default=DEFAULT_VOICE)
    parser.add_argument("--instructions", default=DEFAULT_INSTRUCTIONS)
    args = parser.parse_args()

    if not args.api_key:
        print("ERROR: --api-key or OPENAI_API_KEY env var required", file=sys.stderr)
        sys.exit(1)

    print("1/4 Extracting speech text...")
    speech_text = extract_speech_text(args.input)
    print(f"    Total: {len(speech_text)} chars")

    print("2/4 Splitting into chunks...")
    chunks = split_into_chunks(speech_text)
    print(f"    {len(chunks)} chunks")

    print("3/4 Generating TTS...")
    output_dir = os.path.dirname(args.output)
    chunk_files = []
    for i, chunk in enumerate(chunks):
        out = os.path.join(output_dir, f"_chunk_{i:03d}.mp3")
        print(f"    [{i+1}/{len(chunks)}] {len(chunk)} chars...")
        generate_tts_chunk(chunk, out, args.api_key, args.model, args.voice, args.instructions)
        chunk_files.append(out)

    print("4/4 Merging audio...")
    merge_audio(chunk_files, args.output)

    duration = get_duration(args.output)
    minutes, seconds = int(duration // 60), int(duration % 60)
    print(f"\nDone! {args.output} ({minutes}m {seconds}s)")


if __name__ == "__main__":
    main()
