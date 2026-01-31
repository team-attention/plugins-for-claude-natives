# Gmail CLI Detailed Usage

## List Messages

```bash
# Recent 10 emails
uv run python scripts/list_messages.py --account work --max 10

# Unread emails
uv run python scripts/list_messages.py --account work --query "is:unread"

# From specific sender
uv run python scripts/list_messages.py --account work --query "from:user@example.com"

# Date range
uv run python scripts/list_messages.py --account work --query "after:2024/01/01 before:2024/12/31"

# Filter by label
uv run python scripts/list_messages.py --account work --labels INBOX,IMPORTANT

# Include full content
uv run python scripts/list_messages.py --account work --full

# JSON output
uv run python scripts/list_messages.py --account work --json
```

## Read Messages

```bash
# Read message
uv run python scripts/read_message.py --account work --id <message_id>

# Read entire thread
uv run python scripts/read_message.py --account work --thread <thread_id>

# Save attachments
uv run python scripts/read_message.py --account work --id <message_id> --save-attachments ./downloads
```

## Send Messages

```bash
# New email
uv run python scripts/send_message.py --account work \
    --to "user@example.com" \
    --subject "Hello" \
    --body "Email content here."

# HTML email
uv run python scripts/send_message.py --account work \
    --to "user@example.com" \
    --subject "Announcement" \
    --body "<h1>Title</h1><p>Content</p>" \
    --html

# With attachments
uv run python scripts/send_message.py --account work \
    --to "user@example.com" \
    --subject "File Transfer" \
    --body "Please check the attachments." \
    --attach file1.pdf,file2.xlsx

# Reply
uv run python scripts/send_message.py --account work \
    --to "user@example.com" \
    --subject "Re: Original Subject" \
    --body "Reply content" \
    --reply-to <message_id> \
    --thread <thread_id>

# Save as draft
uv run python scripts/send_message.py --account work \
    --to "user@example.com" \
    --subject "Email to send later" \
    --body "Draft content" \
    --draft
```

## Label and Message Management

```bash
# List labels
uv run python scripts/manage_labels.py --account work list-labels

# Create label
uv run python scripts/manage_labels.py --account work create-label --name "Project/A"

# Mark as read
uv run python scripts/manage_labels.py --account work mark-read --id <message_id>

# Star/unstar
uv run python scripts/manage_labels.py --account work star --id <message_id>
uv run python scripts/manage_labels.py --account work unstar --id <message_id>

# Archive
uv run python scripts/manage_labels.py --account work archive --id <message_id>

# Trash
uv run python scripts/manage_labels.py --account work trash --id <message_id>
uv run python scripts/manage_labels.py --account work untrash --id <message_id>

# Add/remove labels
uv run python scripts/manage_labels.py --account work modify --id <message_id> \
    --add-labels "Label_123,STARRED" --remove-labels "INBOX"

# List drafts
uv run python scripts/manage_labels.py --account work list-drafts

# Send draft
uv run python scripts/manage_labels.py --account work send-draft --draft-id <draft_id>

# View profile
uv run python scripts/manage_labels.py --account work profile
```
