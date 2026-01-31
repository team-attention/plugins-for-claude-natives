# Gmail Search Query Reference

## Basic Queries

| Query | Description |
|-------|-------------|
| `from:user@example.com` | Specific sender |
| `to:user@example.com` | Specific recipient |
| `subject:project` | Contains in subject |
| `is:unread` | Unread |
| `is:starred` | Starred |
| `is:important` | Marked important |
| `has:attachment` | Has attachment |
| `filename:pdf` | PDF attachment |

## Date Related

| Query | Description |
|-------|-------------|
| `after:2024/01/01` | After date |
| `before:2024/12/31` | Before date |
| `older_than:7d` | Older than 7 days |
| `newer_than:1d` | Within 1 day |

## Location Related

| Query | Description |
|-------|-------------|
| `in:inbox` | Inbox |
| `in:sent` | Sent mail |
| `in:drafts` | Drafts |
| `in:trash` | Trash |
| `label:work` | Specific label |

## Compound Query Examples

```
# Unread emails from specific sender
from:boss@company.com is:unread

# Emails with attachments in last 7 days
has:attachment newer_than:7d

# Excel attachments within date range
has:attachment filename:xlsx after:2024/01/01 before:2024/12/31

# Important unread emails
is:unread is:important

# Starred emails with specific label
label:projects is:starred
```
