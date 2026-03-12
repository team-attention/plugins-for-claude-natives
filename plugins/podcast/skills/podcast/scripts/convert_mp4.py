#!/usr/bin/env python3
"""MP3 → MP4 conversion (dark background + title overlay)"""

import argparse
import os
import subprocess
import sys

FONT_PATH = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
BG_COLOR = "0x1a1a2e"
RESOLUTION = "1920x1080"


def escape_drawtext(text):
    """Escape special characters for ffmpeg drawtext filter"""
    text = text.replace("\\", "\\\\")
    text = text.replace("'", "'\\''")
    text = text.replace(":", "\\:")
    text = text.replace(";", "\\;")
    text = text.replace("[", "\\[")
    text = text.replace("]", "\\]")
    text = text.replace("=", "\\=")
    text = text.replace("%", "%%")
    return text


def convert(input_path, output_path, title, subtitle=""):
    """Convert MP3 to MP4 with static title card via ffmpeg"""
    vf_parts = []

    if title:
        escaped_title = escape_drawtext(title)
        vf_parts.append(
            f"drawtext=text='{escaped_title}'"
            f":fontsize=60:fontcolor=white"
            f":x=(w-text_w)/2:y=(h-text_h)/2-40"
            f":fontfile={FONT_PATH}"
        )

    if subtitle:
        escaped_sub = escape_drawtext(subtitle)
        vf_parts.append(
            f"drawtext=text='{escaped_sub}'"
            f":fontsize=36:fontcolor=0xAAAAAA"
            f":x=(w-text_w)/2:y=(h-text_h)/2+40"
            f":fontfile={FONT_PATH}"
        )

    vf = ",".join(vf_parts) if vf_parts else "null"

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c={BG_COLOR}:s={RESOLUTION}:r=1",
        "-i", input_path,
        "-c:v", "libx264", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        "-vf", vf,
        output_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ffmpeg error: {result.stderr[-500:]}", file=sys.stderr)
        sys.exit(1)

    size_mb = os.path.getsize(output_path) / 1024 / 1024
    print(f"Done! {output_path} ({size_mb:.1f} MB)")


def main():
    parser = argparse.ArgumentParser(description="MP3 to MP4 conversion")
    parser.add_argument("--input", required=True, help="Input MP3 path")
    parser.add_argument("--output", required=True, help="Output MP4 path")
    parser.add_argument("--title", default="", help="Video title")
    parser.add_argument("--subtitle", default="", help="Video subtitle")
    args = parser.parse_args()

    convert(args.input, args.output, args.title, args.subtitle)


if __name__ == "__main__":
    main()
