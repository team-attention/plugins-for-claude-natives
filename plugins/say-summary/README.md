# say-summary

A Claude Code plugin that speaks a short summary of Claude's response using macOS text-to-speech.

## Features

- Summarizes Claude's response to 3-10 words using Claude Haiku
- Speaks the summary aloud using macOS `say` command
- Runs in background so it doesn't block Claude Code

## Requirements

- **macOS** (uses the `say` command)
- **Python 3.10+**
- **Claude Code CLI** installed

## Installation

```bash
# Add the marketplace
/plugin marketplace add team-attention/plugins-for-claude-natives

# Install the plugin
/plugin install say-summary

# Run setup to install Python dependencies
~/.claude/plugins/say-summary/scripts/setup.sh
```

Or manually install the dependency:

```bash
pip3 install --user claude-agent-sdk
```

## How It Works

1. When Claude finishes responding (Stop hook), the plugin extracts the last message
2. If the message is longer than 10 words, it uses Claude Haiku to create a short headline
3. The summary is spoken aloud via macOS `say` command

## Configuration

The plugin uses these defaults:
- Speech rate: 200 words per minute
- Model: Claude Haiku (for fast summarization)

## Logs

Logs are written to `/tmp/say-summary.log` for debugging.

## License

MIT
