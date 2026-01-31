# Gmail Plugin for Claude Code

A comprehensive Gmail integration plugin for Claude Code that enables multi-account email management through the Gmail API. Read, search, send, and organize emails directly from your Claude Code sessions.

## Overview

The Gmail plugin provides a complete email management solution for Claude Code, supporting multiple Google accounts with features including:

- **Multi-Account Support**: Manage personal, work, and project-specific Gmail accounts
- **Full Email Operations**: List, read, send, reply, and organize emails
- **Smart Caching**: Local caching for optimized API usage
- **Rate Limiting**: Built-in quota management to prevent API throttling
- **Batch Operations**: Efficient bulk operations for label management and cleanup
- **5-Step Sending Workflow**: Structured email composition with test sends and user confirmation

## Features

### Core Email Operations
- List and search emails with Gmail's powerful query syntax
- Read individual messages and entire threads
- Send new emails with plain text or HTML content
- Reply to existing conversations
- Attach files to outgoing emails
- Save emails as drafts

### Organization & Management
- Create, update, and delete labels
- Mark messages as read/unread
- Star/unstar messages
- Archive and trash messages
- Batch modify labels across multiple messages

### Advanced Features
- **Local Caching**: Reduces API calls by caching message lists and content
- **Quota Management**: Tracks usage against Gmail API limits (250 units/second)
- **Exponential Backoff**: Automatic retry with intelligent delays for rate limiting
- **Batch Processing**: Efficient bulk operations for high-volume tasks

## Prerequisites

Before using this plugin, you need:

1. **Python 3.10+** with `uv` package manager
2. **Google Cloud Project** with Gmail API enabled
3. **OAuth 2.0 credentials** (Desktop application type)

### Required Google OAuth Scopes
- `gmail.modify` - Read, modify, and delete emails
- `gmail.send` - Send emails on behalf of the user
- `gmail.labels` - Manage email labels

## Setup Guide

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click the project selector at the top and select "New Project"
3. Enter a project name (e.g., `gmail-skill`) and click "Create"

### Step 2: Enable Gmail API

1. Navigate to "APIs & Services" > "Library" in the left menu
2. Search for "Gmail API"
3. Click the "Enable" button

### Step 3: Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Select "External" for User Type and click "Create"
3. Fill in the required fields:
   - App name: `Gmail Skill`
   - User support email: Your email address
   - Developer contact: Your email address
4. Click "Save and Continue"
5. Add the following scopes:
   - `https://www.googleapis.com/auth/gmail.modify`
   - `https://www.googleapis.com/auth/gmail.send`
   - `https://www.googleapis.com/auth/gmail.labels`
6. Add your Gmail address as a test user
7. Click "Save and Continue"

### Step 4: Create OAuth Client ID

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Select "Desktop app" as the application type
4. Enter a name (e.g., `Gmail Skill Client`)
5. Click "Create"
6. Download the JSON file

### Step 5: Configure the Plugin

```bash
# Navigate to the skill directory
cd .claude/skills/gmail

# Move the downloaded credentials file
mv ~/Downloads/client_secret_*.json references/credentials.json

# Copy the default accounts configuration
cp assets/accounts.default.yaml accounts.yaml

# Edit accounts.yaml with your account information
```

### Step 6: Authenticate Accounts

```bash
# Authenticate each account
uv run python scripts/setup_auth.py --account personal
uv run python scripts/setup_auth.py --account work

# Verify registered accounts
uv run python scripts/setup_auth.py --list
```

When the browser opens:
1. Log in to your Google account
2. If you see "This app isn't verified", click "Advanced" > "Continue"
3. Approve all permission requests

## Usage Examples

### List Messages

```bash
# List recent 10 emails
uv run python scripts/list_messages.py --account work --max 10

# List unread emails
uv run python scripts/list_messages.py --account work --query "is:unread"

# Search by sender
uv run python scripts/list_messages.py --account work --query "from:user@example.com"

# Search by date range
uv run python scripts/list_messages.py --account work --query "after:2024/01/01 before:2024/12/31"

# Filter by label
uv run python scripts/list_messages.py --account work --labels INBOX,IMPORTANT

# Include full message content
uv run python scripts/list_messages.py --account work --full

# Output as JSON
uv run python scripts/list_messages.py --account work --json
```

### Read Messages

```bash
# Read a specific message
uv run python scripts/read_message.py --account work --id <message_id>

# Read an entire thread
uv run python scripts/read_message.py --account work --thread <thread_id>

# Save attachments to a directory
uv run python scripts/read_message.py --account work --id <message_id> --save-attachments ./downloads
```

### Send Messages

```bash
# Send a new email
uv run python scripts/send_message.py --account work \
    --to "user@example.com" \
    --subject "Hello" \
    --body "Email content here."

# Send HTML email
uv run python scripts/send_message.py --account work \
    --to "user@example.com" \
    --subject "Announcement" \
    --body "<h1>Title</h1><p>Content</p>" \
    --html

# Send with attachments
uv run python scripts/send_message.py --account work \
    --to "user@example.com" \
    --subject "File Transfer" \
    --body "Please check the attachments." \
    --attach file1.pdf,file2.xlsx

# Reply to a message
uv run python scripts/send_message.py --account work \
    --to "user@example.com" \
    --subject "Re: Original Subject" \
    --body "Reply content" \
    --reply-to <message_id> \
    --thread <thread_id>

# Save as draft
uv run python scripts/send_message.py --account work \
    --to "user@example.com" \
    --subject "Draft Email" \
    --body "Draft content" \
    --draft
```

### Manage Labels and Messages

```bash
# List all labels
uv run python scripts/manage_labels.py --account work list-labels

# Create a new label
uv run python scripts/manage_labels.py --account work create-label --name "Project/A"

# Mark as read
uv run python scripts/manage_labels.py --account work mark-read --id <message_id>

# Star/unstar messages
uv run python scripts/manage_labels.py --account work star --id <message_id>
uv run python scripts/manage_labels.py --account work unstar --id <message_id>

# Archive a message
uv run python scripts/manage_labels.py --account work archive --id <message_id>

# Move to trash
uv run python scripts/manage_labels.py --account work trash --id <message_id>
uv run python scripts/manage_labels.py --account work untrash --id <message_id>

# Modify labels
uv run python scripts/manage_labels.py --account work modify --id <message_id> \
    --add-labels "Label_123,STARRED" --remove-labels "INBOX"

# List drafts
uv run python scripts/manage_labels.py --account work list-drafts

# Send a draft
uv run python scripts/manage_labels.py --account work send-draft --draft-id <draft_id>

# View profile information
uv run python scripts/manage_labels.py --account work profile
```

## 5-Step Email Sending Workflow

When Claude Code sends emails, it follows a structured 5-step workflow to ensure accuracy and prevent mistakes:

| Step | Task | Key Action |
|------|------|------------|
| 1 | **Gather Context** | Run parallel exploration tasks: recipient info, related projects, background context |
| 2 | **Check Previous Conversations** | Search `"to:recipient OR from:recipient newer_than:90d"` and ask user about thread selection |
| 3 | **Draft Email** | Compose draft based on context and templates, ask user for feedback |
| 4 | **Test Send** | Send `[TEST]` email to user's own address for review |
| 5 | **Actual Send** | Send to recipient after user confirmation |

### Workflow Example: "Send a meeting email to John"

1. **Create 5 Tasks** using TaskCreate
2. **Step 1**: Run parallel Explore tasks
   - Search for John's contact info in `partners/`, `projects/`, `context.md`
   - Search for meeting context (calendar, recent notes)
3. **Step 2**: Search `"to:john@company.com OR from:john@company.com"`
   - If previous conversation exists, ask user whether to reply or create new email
4. **Step 3**: Draft email using appropriate template from `assets/email-templates.md`
   - Ask user to review and approve
5. **Step 4**: Test send to user's own email address
   - Request confirmation after user reviews
6. **Step 5**: Send to John
   - Report completion

**Signature**: All outgoing emails include the signature:
```
---
Sent with Claude Code
```

## accounts.yaml Configuration

The `accounts.yaml` file stores metadata about your Gmail accounts:

```yaml
# Gmail Account Settings
# Token files are stored separately in accounts/{name}.json

accounts:
  # Personal Gmail account
  personal:
    email: your-personal@gmail.com
    description: Personal Gmail

  # Work/Business account
  work:
    email: your-work@company.com
    description: Work account

  # Additional account example
  project:
    email: project@domain.com
    description: For specific project
```

After editing `accounts.yaml`, authenticate each account:
```bash
uv run python scripts/setup_auth.py --account personal
uv run python scripts/setup_auth.py --account work
```

## Available Scripts

### Main Scripts

| Script | Description |
|--------|-------------|
| `setup_auth.py` | OAuth authentication setup for new accounts |
| `list_messages.py` | List and search emails with various filters |
| `read_message.py` | Read individual messages or entire threads |
| `send_message.py` | Send new emails, replies, or save as drafts |
| `manage_labels.py` | Label management and message organization |
| `gmail_client.py` | Core Gmail API client library |

### Core Modules (scripts/core/)

| Module | Description |
|--------|-------------|
| `quota_manager.py` | Gmail API quota tracking and rate limiting |
| `retry_handler.py` | Exponential backoff for API error handling |
| `cache_manager.py` | Local caching for API response optimization |
| `batch_processor.py` | Efficient bulk operations for multiple messages |

## Gmail Search Query Examples

### Basic Queries

| Query | Description |
|-------|-------------|
| `from:user@example.com` | From specific sender |
| `to:user@example.com` | To specific recipient |
| `subject:project` | Contains word in subject |
| `is:unread` | Unread messages |
| `is:starred` | Starred messages |
| `is:important` | Marked as important |
| `has:attachment` | Has attachments |
| `filename:pdf` | PDF attachments |

### Date Filters

| Query | Description |
|-------|-------------|
| `after:2024/01/01` | After specific date |
| `before:2024/12/31` | Before specific date |
| `older_than:7d` | Older than 7 days |
| `newer_than:1d` | Within last day |

### Location Filters

| Query | Description |
|-------|-------------|
| `in:inbox` | In inbox |
| `in:sent` | In sent mail |
| `in:drafts` | In drafts |
| `in:trash` | In trash |
| `label:work` | Has specific label |

### Compound Query Examples

```bash
# Unread from specific sender
from:boss@company.com is:unread

# Attachments in last 7 days
has:attachment newer_than:7d

# Excel files in date range
has:attachment filename:xlsx after:2024/01/01 before:2024/12/31

# Important unread emails
is:unread is:important

# Starred with specific label
label:projects is:starred
```

## Troubleshooting

### "credentials.json file not found"

Ensure you have:
1. Downloaded the OAuth client ID JSON from Google Cloud Console
2. Saved it to `references/credentials.json`

### "Token has expired"

Tokens auto-refresh, but if that fails:
```bash
uv run python scripts/setup_auth.py --account <name>
```

### "This app isn't verified"

This is normal for personal OAuth apps. Click "Advanced" > "Continue" during authentication.

### "Insufficient permissions"

Ensure these scopes are enabled in your OAuth consent screen:
- `gmail.modify`
- `gmail.send`
- `gmail.labels`

### "Rate limit exceeded"

The plugin includes built-in rate limiting. If you hit limits:
- Wait a few seconds before retrying
- The exponential backoff will handle automatic retries
- Check quota status with `get_quota_status()` method

### "Account not found"

1. Verify the account exists in `accounts.yaml`
2. Check that the token file exists in `accounts/{name}.json`
3. Re-run authentication if needed

## Security Notes

### Credential Storage
- **credentials.json**: Contains your OAuth client ID and secret. Keep this secure and never commit to version control.
- **accounts/*.json**: Contains refresh tokens for each account. These are gitignored by default.
- **accounts.yaml**: Contains only email addresses and descriptions (no secrets).

### Best Practices
1. Add `references/credentials.json` and `accounts/` to your `.gitignore`
2. Never share or commit token files
3. Use separate Google Cloud projects for development and production
4. Regularly review OAuth consent screen test users
5. Revoke access from [Google Account Security](https://myaccount.google.com/permissions) if needed

### Data Privacy
- Emails are accessed only when explicitly requested
- Caching is local to your machine
- No data is sent to external services beyond the Gmail API
- Test sends go to your own email address for review

## File Structure

```
skills/gmail/
├── SKILL.md                    # Skill configuration for Claude Code
├── accounts.yaml               # Account metadata (emails, descriptions)
├── scripts/
│   ├── gmail_client.py         # Core Gmail API client
│   ├── list_messages.py        # List/search messages CLI
│   ├── read_message.py         # Read messages CLI
│   ├── send_message.py         # Send messages CLI
│   ├── manage_labels.py        # Label management CLI
│   ├── setup_auth.py           # OAuth setup CLI
│   └── core/
│       ├── __init__.py
│       ├── batch_processor.py  # Bulk operations
│       ├── cache_manager.py    # Local caching
│       ├── quota_manager.py    # Rate limiting
│       └── retry_handler.py    # Error handling
├── references/
│   ├── credentials.json        # OAuth Client ID (gitignored)
│   ├── setup-guide.md          # Detailed setup instructions
│   ├── cli-usage.md            # CLI command reference
│   └── search-queries.md       # Gmail query syntax reference
├── assets/
│   ├── accounts.default.yaml   # Default accounts template
│   ├── email-templates.md      # Email body templates
│   └── signatures.md           # Signature templates
└── accounts/                   # Per-account tokens (gitignored)
    ├── personal.json
    └── work.json
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GMAIL_SKILL_PATH` | Auto-detected | Skill root path |
| `GMAIL_TIMEOUT` | `30` | API request timeout (seconds) |
| `GMAIL_CACHE_DIR` | `.cache/gmail` | Cache directory location |
| `GMAIL_ENABLE_CACHE` | `true` | Enable/disable caching |
| `GMAIL_ENABLE_QUOTA` | `true` | Enable/disable quota management |

## License

This plugin is part of the [plugins-for-claude-natives](https://github.com/team-attention/plugins-for-claude-natives) project.
