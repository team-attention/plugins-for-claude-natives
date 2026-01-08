#!/usr/bin/env python3
# /// script
# dependencies = ["mcp>=1.0.0"]
# ///
"""
Interactive Review MCP Server

Provides the start_review tool that:
1. Parses markdown content into reviewable blocks
2. Generates an interactive HTML UI
3. Serves it via a local HTTP server
4. Opens the browser automatically
5. Waits for user feedback
6. Returns structured review results
"""

import asyncio
import json
import os
import signal
import socket
import sys
import tempfile
import threading
import uuid
import webbrowser
from dataclasses import asdict
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from web_ui import parse_markdown, generate_html


# Global state for the HTTP server
_review_result: dict | None = None
_result_event = threading.Event()


def find_free_port() -> int:
    """Find a free port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        return s.getsockname()[1]


class ReviewHTTPHandler(SimpleHTTPRequestHandler):
    """HTTP handler for serving the review UI and receiving results."""

    def __init__(self, *args, review_dir: str, **kwargs):
        self.review_dir = review_dir
        super().__init__(*args, directory=review_dir, **kwargs)

    def do_POST(self):
        """Handle POST request for submitting review results."""
        global _review_result

        if self.path == '/submit':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            try:
                _review_result = json.loads(post_data.decode('utf-8'))
                _result_event.set()

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'{"status": "ok"}')
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        """Suppress logging to stderr."""
        pass


def make_handler(review_dir: str):
    """Factory to create handler with review_dir bound."""
    def handler(*args, **kwargs):
        return ReviewHTTPHandler(*args, review_dir=review_dir, **kwargs)
    return handler


async def start_review_impl(content: str, title: str = "Review") -> dict[str, Any]:
    """
    Implementation of the start_review tool.

    Args:
        content: Markdown content to review
        title: Title for the review UI

    Returns:
        Review results with status, items, and summary
    """
    global _review_result, _result_event

    # Reset state
    _review_result = None
    _result_event.clear()

    # Create temp directory
    review_id = str(uuid.uuid4())[:8]
    review_dir = Path(tempfile.gettempdir()) / f"claude-review-{review_id}"
    review_dir.mkdir(parents=True, exist_ok=True)

    server = None
    try:
        # Parse markdown
        blocks = parse_markdown(content)

        if not blocks:
            return {
                "status": "error",
                "message": "No reviewable content found in the markdown"
            }

        # Find a free port
        port = find_free_port()

        # Generate HTML
        html_content = generate_html(title, content, blocks, port)
        html_path = review_dir / "index.html"
        html_path.write_text(html_content, encoding='utf-8')

        # Save input for reference
        input_data = {
            "version": "1.0",
            "title": title,
            "content": content,
            "blocks": [asdict(b) for b in blocks]
        }
        (review_dir / "input.json").write_text(
            json.dumps(input_data, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )

        # Start HTTP server in a thread
        server = HTTPServer(('localhost', port), make_handler(str(review_dir)))
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()

        # Open browser
        url = f"http://localhost:{port}/index.html"
        webbrowser.open(url)

        # Wait for result (timeout: 5 minutes)
        timeout = 300
        result_received = await asyncio.get_event_loop().run_in_executor(
            None, lambda: _result_event.wait(timeout)
        )

        if not result_received:
            return {
                "status": "timeout",
                "message": "Review timed out after 5 minutes"
            }

        if _review_result is None:
            return {
                "status": "error",
                "message": "No result received"
            }

        # Enrich result with summary
        items = _review_result.get("items", [])
        approved = sum(1 for item in items if item.get("checked", False))
        rejected = len(items) - approved
        has_comments = sum(1 for item in items if item.get("comment", "").strip())

        return {
            "status": _review_result.get("status", "unknown"),
            "items": items,
            "summary": {
                "total": len(items),
                "approved": approved,
                "rejected": rejected,
                "has_comments": has_comments
            }
        }

    finally:
        # Shutdown server
        if server:
            try:
                server.shutdown()
            except Exception as e:
                print(f"Error shutting down HTTP server: {e}", file=sys.stderr)

        # Cleanup temp directory
        try:
            import shutil
            shutil.rmtree(review_dir, ignore_errors=True)
        except Exception:
            pass


# Create MCP server
app = Server("interactive-review")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="start_review",
            description="""Open an interactive web UI to review markdown content.

The user can:
- Check/uncheck items to approve or reject them
- Add comments to any item
- Submit the review when done

Returns structured feedback with approval status and comments for each item.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "Markdown content to review (plans, documents, etc.)"
                    },
                    "title": {
                        "type": "string",
                        "description": "Title for the review UI",
                        "default": "Review"
                    }
                },
                "required": ["content"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    if name == "start_review":
        content = arguments.get("content", "")
        title = arguments.get("title", "Review")

        result = await start_review_impl(content, title)

        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, ensure_ascii=False)
        )]

    return [TextContent(
        type="text",
        text=json.dumps({"error": f"Unknown tool: {name}"})
    )]


def setup_signal_handlers():
    """Set up signal handlers for graceful shutdown."""
    def handle_shutdown(signum, frame):
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGHUP, handle_shutdown)
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)


async def main():
    """Main entry point."""
    setup_signal_handlers()

    try:
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    except (BrokenPipeError, ConnectionResetError, EOFError):
        # Parent process closed the pipe - exit gracefully
        pass
    except KeyboardInterrupt:
        pass
    finally:
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
