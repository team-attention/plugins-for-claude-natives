---
name: gmail
description: This skill should be used when the user asks to "check email", "read emails", "send email", "reply to email", "search inbox", or manages Gmail. Supports multi-account Gmail integration for reading, searching, sending, and label management.
---

# Gmail Skill

Manage emails through Gmail API - read, search, send, and organize across multiple Google accounts.

## Account Setup

**Before running any command, read `accounts.yaml` to check registered accounts.**

> If `accounts.yaml` is missing or empty → Read `references/setup-guide.md` for initial setup

```yaml
# accounts.yaml example
accounts:
  personal:
    email: user@gmail.com
    description: Personal Gmail
  work:
    email: user@company.com
    description: Work account
```

## Email Sending Workflow (5 Steps)

When sending emails, **create 5 Tasks with TaskCreate** and execute sequentially:

| Step | Task | Key Action |
|------|------|----------|
| 1 | Gather context | Run Explore SubAgents **in parallel**: recipient info, related projects, background context |
| 2 | Check previous conversations | Search `--query "to:recipient OR from:recipient newer_than:90d"` → AskUserQuestion for thread selection |
| 3 | Draft email | Compose draft → AskUserQuestion for feedback |
| 4 | Test send | Send `[TEST]` email to user's own address → Open in Gmail web → Request confirmation |
| 5 | Actual send | Send to recipient → Report completion |

**Signature**: Append `---\nSent with Claude Code` to all outgoing emails

### Workflow Example: "Send a meeting email to John"

```
1. Create 5 Tasks
2. Step 1: Run parallel Explore SubAgents
   - Search recipient (John) info (partners/, projects/, context.md, etc.)
   - Search meeting context (calendar, recent meeting notes, etc.)
3. Step 2: Search "to:john@company.com OR from:john@company.com"
   → If previous conversation exists, AskUserQuestion (reply/new email)
4. Step 3: Draft email → AskUserQuestion (proceed/revise)
5. Step 4: Test send to my email → Open in Gmail web (`open "https://mail.google.com/mail/u/0/#inbox/{message_id}"`) → Request confirmation
6. Step 5: Actual send → Done
```

## CLI Quick Reference

```bash
# List messages
uv run python scripts/list_messages.py --account work --query "is:unread" --max 10

# Send email
uv run python scripts/send_message.py --account work --to "user@example.com" --subject "Subject" --body "Content"

# Check profile
uv run python scripts/manage_labels.py --account work profile
```

> Detailed CLI usage: `references/cli-usage.md`
> Search query reference: `references/search-queries.md`

## View Email in Web

After sending, use the returned Message ID to view directly in Gmail web:

```bash
# URL format
https://mail.google.com/mail/u/0/#inbox/{message_id}

# Example: Open in browser after test send
open "https://mail.google.com/mail/u/0/#inbox/19c145bbd47ddd01"
```

> **Note**: `u/0` is the first logged-in account, `u/1` is the second account

## File Structure

```
skills/gmail/
├── SKILL.md
├── accounts.yaml           # Account metadata
├── scripts/                # CLI scripts
├── references/
│   ├── setup-guide.md      # Initial setup guide
│   ├── cli-usage.md        # Detailed CLI usage
│   ├── search-queries.md   # Search query reference
│   └── credentials.json    # OAuth Client ID (gitignore)
├── assets/
│   ├── accounts.default.yaml  # Account config template
│   ├── email-templates.md     # Email body templates
│   └── signatures.md          # Signature templates (Plain/HTML)
└── accounts/               # Per-account tokens (gitignore)
```

## Error Handling

| Situation | Resolution |
|-----------|------------|
| accounts.yaml missing | Read `references/setup-guide.md` for initial setup |
| Token missing | Guide user to run `setup_auth.py --account <name>` |
| Token expired | Auto-refresh; if failed, guide re-authentication |
