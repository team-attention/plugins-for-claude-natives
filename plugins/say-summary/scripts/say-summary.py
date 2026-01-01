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

LOG_FILE = Path("/tmp/say-summary.log")


def log(message: str) -> None:
    """Write message to log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")


def get_project_dir() -> Path | None:
    """Find Claude project directory for current working directory."""
    cwd = os.getcwd()
    project_dir_name = cwd.replace("/", "-")
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

        for line in reversed(lines):
            try:
                data = json.loads(line)
                message = data.get("message", {})

                if message and message.get("role") == "assistant":
                    content = message.get("content", [])

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


def extract_first_sentence(text: str) -> str:
    """Fallback: extract first sentence from text."""
    import re
    match = re.match(r"^(.*?[.!?])", text, re.DOTALL)
    if match:
        sentence = match.group(1).strip()
        if len(sentence) >= 3:
            return sentence
    return text[:80].strip()


async def summarize_with_haiku(text: str) -> str:
    """Summarize message to 10 words or less using Claude Haiku."""
    # Return as-is if already 10 words or less
    if len(text.split()) <= 10:
        return text.strip()

    try:
        from claude_agent_sdk import (
            AssistantMessage,
            ClaudeAgentOptions,
            TextBlock,
            query,
        )
    except ImportError:
        log("claude-agent-sdk not installed, using fallback")
        return extract_first_sentence(text)

    truncated = text[:500] if len(text) > 500 else text

    system_prompt = (
        "You are a headline writer. Output ONLY a 3-10 word headline. "
        "No questions. No commentary. No offers to help. Just the headline."
    )

    options = ClaudeAgentOptions(
        model="haiku",
        system_prompt=system_prompt,
        allowed_tools=[],
        max_turns=1,
    )

    response_text = ""
    try:
        async for message in query(prompt=truncated, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        response_text += block.text
                        return response_text.strip()
    except Exception as e:
        log(f"Haiku summarization failed: {e}")
        return extract_first_sentence(text)

    return response_text.strip() if response_text else extract_first_sentence(text)


def speak(text: str) -> None:
    """Speak text via macOS say command (background)."""
    subprocess.Popen(
        ["nohup", "say", "-r", "200", text],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


async def async_main() -> None:
    log("=== HOOK START ===")
    log(f"PWD: {os.getcwd()}")

    project_dir = get_project_dir()
    if not project_dir:
        log("Project dir not found")
        return
    log(f"Project dir: {project_dir}")

    transcript_path = get_latest_transcript(project_dir)
    if not transcript_path:
        log("No transcript file found")
        return
    log(f"Transcript: {transcript_path.name}")

    last_message = extract_last_assistant_message(transcript_path)
    if not last_message:
        log("No assistant message found")
        return
    log(f"Found message ({len(last_message)} chars)")

    summary = await summarize_with_haiku(last_message)
    log(f"Summary: {summary}")

    speak(summary)

    log("=== HOOK END ===")


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
