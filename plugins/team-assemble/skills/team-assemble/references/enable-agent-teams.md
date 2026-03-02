# Enable Agent Teams in Claude Code

Agent teams are experimental and disabled by default. You must enable them before using the team-assemble skill.

## Quick Setup

Add this to your `settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

### Where is settings.json?

| Scope | Path |
|-------|------|
| User (global) | `~/.claude/settings.json` |
| Project | `.claude/settings.json` (in project root) |

User settings apply to all projects. Project settings apply only to that project.

### Alternative: Environment Variable

Set it in your shell profile (`~/.zshrc`, `~/.bashrc`, etc.):

```bash
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
```

Then restart your terminal or run `source ~/.zshrc`.

## Verify It's Enabled

After setting, start Claude Code and ask it to create a team. If agent teams are not enabled, Claude Code will not have access to TeamCreate, SendMessage, and related tools.

## Display Modes

Agent teams support two display modes:

| Mode | Description | Setup |
|------|-------------|-------|
| **in-process** (default) | All teammates in one terminal. Use Shift+Down to cycle. | Works everywhere |
| **split panes** | Each teammate gets its own pane | Requires tmux or iTerm2 |

To set a display mode, add to `settings.json`:

```json
{
  "teammateMode": "in-process"
}
```

Or pass as a flag:

```bash
claude --teammate-mode in-process
```

### Split Pane Setup (Optional)

For split-pane mode, install one of:

- **tmux**: `brew install tmux` (macOS) or your system's package manager
- **iTerm2**: install the [`it2` CLI](https://github.com/mkusaka/it2), then enable Python API in iTerm2 → Settings → General → Magic → Enable Python API

> Note: Split-pane mode is not supported in VS Code's integrated terminal, Windows Terminal, or Ghostty.

## Key Controls (In-Process Mode)

| Key | Action |
|-----|--------|
| Shift+Down | Cycle through teammates |
| Enter | View a teammate's session |
| Escape | Interrupt teammate's current turn |
| Ctrl+T | Toggle task list |

## Known Limitations

- **No session resumption**: `/resume` and `/rewind` do not restore in-process teammates
- **One team per session**: clean up the current team before starting a new one
- **No nested teams**: teammates cannot spawn their own teams
- **Permissions inherited**: all teammates start with the lead's permission mode
- **Shutdown can be slow**: teammates finish their current operation before shutting down

## Official Documentation

For the latest information: https://code.claude.com/docs/en/agent-teams
