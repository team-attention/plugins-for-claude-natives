#!/usr/bin/env python3
"""
Stop hook: Summarizes and speaks the last Claude response.

- Extracts the last assistant message from transcript
- Uses Claude Agent SDK (Haiku) to summarize in 10 words or less
- Speaks the summary via macOS say command
- Runs in background so hook exits immediately
"""

import asyncio
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

from claude_agent_sdk import (AssistantMessage, ClaudeAgentOptions, TextBlock,
                              query)

LOG_FILE = Path("/tmp/speak-hook.log")


def log(message: str) -> None:
    """Write message to log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")


def get_project_dir() -> Path | None:
    """Find Claude project directory for current working directory."""
    cwd = os.getcwd()
    # /Users/bong/.path/to/project -> -Users-bong--path-to-project
    project_dir_name = cwd.replace("/", "-").replace(".", "-")
    claude_project_dir = Path.home() / ".claude" / "projects" / project_dir_name

    if claude_project_dir.is_dir():
        return claude_project_dir
    return None


def get_latest_transcript(project_dir: Path) -> Path | None:
    """Find most recently modified transcript file."""
    jsonl_files = list(project_dir.glob("*.jsonl"))
    if not jsonl_files:
        return None

    return max(jsonl_files, key=lambda f: f.stat().st_mtime)


def extract_last_assistant_message(transcript_path: Path) -> str | None:
    """Extract last assistant message from transcript."""
    try:
        with open(transcript_path, "r") as f:
            lines = f.readlines()

        # Search in reverse order
        for line in reversed(lines):
            try:
                data = json.loads(line)
                message = data.get("message", {})

                if message and message.get("role") == "assistant":
                    content = message.get("content", [])

                    # Extract text type items
                    text_parts = [
                        item.get("text", "")
                        for item in content
                        if isinstance(item, dict) and item.get("type") == "text"
                    ]

                    full_text = "".join(text_parts)
                    if full_text:
                        return full_text

            except json.JSONDecodeError:
                continue

    except Exception as e:
        log(f"Error reading transcript: {e}")

    return None


async def summarize_with_haiku(text: str) -> str:
    """Summarize message to 10 words or less using Claude Haiku."""
    # Return as-is if already 10 words or less
    if len(text.split()) <= 10:
        return text.strip()

    # Truncate for faster processing
    truncated = text[:500] if len(text) > 500 else text

    system_prompt = "You are a headline writer. Output ONLY a 3-10 word headline. No questions. No commentary. No offers to help. Just the headline. If the text contains both English and Korean, write the headline in Korean."

    options = ClaudeAgentOptions(
        model="haiku",
        system_prompt=system_prompt,
        allowed_tools=[],
        max_turns=1
    )

    response_text = ""
    try:
        async for message in query(prompt=f"요약할 텍스트: {truncated}", options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        response_text += block.text
                        # Return immediately after first response
                        return response_text.strip()
    except Exception as e:
        log(f"Haiku summarization failed: {e}")
        return text[:50].strip()

    return response_text.strip() if response_text else text[:50].strip()


def detect_korean(text: str) -> bool:
    """Check if text contains Korean characters."""
    for char in text:
        if '\uac00' <= char <= '\ud7a3':  # 한글 음절
            return True
        if '\u1100' <= char <= '\u11ff':  # 한글 자모
            return True
    return False


def speak(text: str) -> None:
    """Speak text via macOS say command (background).

    - Uses rate -r 190 for natural pace
    - Detects language: Korean uses Yuna, English uses Samantha
    """
    cmd = ["nohup", "say", "-r", "190"]

    if detect_korean(text):
        cmd.extend(["-v", "Yuna"])
    else:
        cmd.extend(["-v", "Samantha"])

    cmd.append(text)

    subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )


async def async_main() -> None:
    log("=== HOOK START ===")
    log(f"PWD: {os.getcwd()}")

    # 1. Find project directory
    project_dir = get_project_dir()
    if not project_dir:
        log("Project dir not found")
        return
    log(f"Project dir: {project_dir}")

    # 2. Find latest transcript file
    transcript_path = get_latest_transcript(project_dir)
    if not transcript_path:
        log("No transcript file found")
        return
    log(f"Transcript: {transcript_path.name}")

    # 3. Extract last assistant message
    last_message = extract_last_assistant_message(transcript_path)
    if not last_message:
        log("No assistant message found")
        return
    log(f"Found message ({len(last_message)} chars)")

    # 4. Summarize with Haiku
    summary = await summarize_with_haiku(last_message)
    log(f"Summary: {summary}")

    # 5. Speak summary
    speak(summary)

    log("=== HOOK END ===")


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
