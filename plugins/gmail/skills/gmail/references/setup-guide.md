# Gmail Skill Initial Setup Guide

Follow this guide if accounts.yaml is missing or no accounts are registered.

---

## 1. Google Cloud Project Setup

### 1.1 Create Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click project selector at top → "New Project"
3. Enter project name (e.g., `gmail-skill`)
4. Click "Create"

### 1.2 Enable Gmail API

1. Left menu → "APIs & Services" → "Library"
2. Search for "Gmail API"
3. Click "Enable" button

### 1.3 Configure OAuth Consent Screen

1. "APIs & Services" → "OAuth consent screen"
2. User Type: Select "External" → "Create"
3. Enter app information:
   - App name: `Gmail Skill`
   - User support email: Your email
   - Developer contact: Your email
4. "Save and Continue"
5. Add scopes:
   - `https://www.googleapis.com/auth/gmail.modify`
   - `https://www.googleapis.com/auth/gmail.send`
   - `https://www.googleapis.com/auth/gmail.labels`
6. Add test users (your Gmail address)
7. "Save and Continue"

### 1.4 Create OAuth Client ID

1. "APIs & Services" → "Credentials"
2. "Create Credentials" → "OAuth client ID"
3. Application type: **Desktop app**
4. Name: `Gmail Skill Client`
5. Click "Create"
6. Click **Download JSON**

### 1.5 Save credentials.json

```bash
# Move downloaded file to references/credentials.json
mv ~/Downloads/client_secret_*.json .claude/skills/gmail/references/credentials.json
```

---

## 2. Account Setup

### 2.1 Create accounts.yaml

```bash
cd .claude/skills/gmail

# Copy default template
cp assets/accounts.default.yaml accounts.yaml
```

### 2.2 Edit accounts.yaml

```yaml
# accounts.yaml
accounts:
  personal:
    email: your-personal@gmail.com
    description: Personal Gmail
  work:
    email: your-work@company.com
    description: Work account
```

---

## 3. Account Authentication

### 3.1 Install Dependencies

```bash
cd .claude/skills/gmail
uv sync
```

### 3.2 Authenticate Each Account

```bash
# Authenticate personal account
uv run python scripts/setup_auth.py --account personal

# Authenticate work account
uv run python scripts/setup_auth.py --account work
```

When browser opens:
1. Log in to Google account
2. Approve permission request
3. "This app isn't verified" → "Advanced" → "Continue"
4. Allow all permissions

### 3.3 Verify Authentication

```bash
# List registered accounts
uv run python scripts/setup_auth.py --list
```

Example output:
```
📋 Registered accounts:

   ✅ personal
      Email: your-personal@gmail.com
      Description: Personal Gmail

   ✅ work
      Email: your-work@company.com
      Description: Work account
```

---

## 4. Test

```bash
# Test mail listing
uv run python scripts/list_messages.py --account personal --max 5

# Check profile
uv run python scripts/manage_labels.py --account personal profile
```

---

## Troubleshooting

### "credentials.json file not found"

→ Check steps 1.4-1.5. Download OAuth client ID JSON and save to `references/credentials.json`.

### "Token has expired"

→ If auto-refresh fails, re-authenticate:
```bash
uv run python scripts/setup_auth.py --account <name>
```

### "This app isn't verified"

→ Add your email as a test user in OAuth consent screen.

### "Insufficient permissions"

→ Add required scopes in OAuth consent screen:
- `gmail.modify`
- `gmail.send`
- `gmail.labels`

---

## File Checklist

Verify after setup:

```
.claude/skills/gmail/
├── accounts.yaml              ✅ Account information
├── references/
│   └── credentials.json       ✅ OAuth Client ID
└── accounts/
    ├── personal.json          ✅ personal token
    └── work.json              ✅ work token
```

Setup is complete when all files exist.
