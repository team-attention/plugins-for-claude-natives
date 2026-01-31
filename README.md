# Plugins for Claude Natives

A collection of Claude Code plugins for power users who want to extend Claude Code's capabilities beyond the defaults.

## Table of Contents

- [Quick Start](#quick-start)
- [Available Plugins](#available-plugins)
- [Plugin Details](#plugin-details)
  - [agent-council](#agent-council) - Get consensus from multiple AI models
  - [clarify](#clarify) - Transform vague requirements into specs
  - [dev](#dev) - Community scanning + technical decision-making
  - [doubt](#doubt) - Force Claude to re-validate responses
  - [interactive-review](#interactive-review) - Review plans with a web UI
  - [say-summary](#say-summary) - Hear responses via text-to-speech
  - [youtube-digest](#youtube-digest) - Summarize and quiz on YouTube videos
  - [gmail](#gmail) - Multi-account Gmail integration
  - [google-calendar](#google-calendar) - Multi-account calendar integration
  - [kakaotalk](#kakaotalk) - Send/read KakaoTalk messages on macOS
  - [session-wrap](#session-wrap) - Session wrap-up + history analysis toolkit
- [Contributing](#contributing)
- [License](#license)

---

## Quick Start

```bash
# Add this marketplace to Claude Code
/plugin marketplace add team-attention/plugins-for-claude-natives

# Install any plugin
/plugin install <plugin-name>
```

---

## Available Plugins

| Plugin | Description |
|--------|-------------|
| [agent-council](./plugins/agent-council/) | Collect and synthesize opinions from multiple AI agents (Gemini, GPT, Codex) |
| [clarify](./plugins/clarify/) | Transform vague requirements into precise specifications through iterative questioning |
| [dev](./plugins/dev/) | Developer workflow: community opinion scanning and technical decision analysis |
| [doubt](./plugins/doubt/) | Force Claude to re-validate its response when `!rv` is in your prompt |
| [interactive-review](./plugins/interactive-review/) | Interactive markdown review with web UI for visual plan/document approval |
| [say-summary](./plugins/say-summary/) | Speaks a short summary of Claude's response using macOS TTS (Korean/English) |
| [youtube-digest](./plugins/youtube-digest/) | Summarize YouTube videos with transcript, insights, Korean translation, and quizzes |
| [gmail](./plugins/gmail/) | Multi-account Gmail integration with email reading, searching, sending, and management |
| [google-calendar](./plugins/google-calendar/) | Multi-account Google Calendar integration with parallel querying and conflict detection |
| [kakaotalk](./plugins/kakaotalk/) | Send and read KakaoTalk messages on macOS using Accessibility API |
| [session-wrap](./plugins/session-wrap/) | Session wrap-up, history analysis, and session validation toolkit |

## Plugin Details

### agent-council

![Demo](./assets/agent-council.gif)

**Summon multiple AI models to debate your question and reach a consensus.**

When you're facing a tough decision or want diverse perspectives, this plugin queries multiple AI agents (Gemini CLI, GPT, Codex) in parallel and synthesizes their opinions into a single, balanced answer.

**Trigger phrases:**
- "summon the council"
- "ask other AIs"
- "what do other models think?"

**How it works:**
1. Your question is sent to multiple AI agents simultaneously
2. Each agent provides its perspective
3. Claude synthesizes the responses into a consensus view with noted disagreements

```bash
# Example
User: "summon the council - should I use TypeScript or JavaScript for my new project?"
```

---

### clarify

![Demo](./assets/clarify.gif)

**Turn vague requirements into precise, actionable specifications.**

Before writing code based on ambiguous instructions, this plugin conducts a structured interview to extract exactly what you need. No more assumptions, no more rework.

**Trigger phrases:**
- "/clarify"
- "clarify requirements"
- "what do I mean by..."

**The process:**
1. **Capture** - Record the original requirement verbatim
2. **Question** - Ask targeted multiple-choice questions to resolve ambiguities
3. **Compare** - Present before/after showing the transformation
4. **Save** - Optionally save the clarified spec to a file

**Example transformation:**

| Before | After |
|--------|-------|
| "Add a login feature" | Goal: Add username/password login with self-registration. Scope: Login, logout, registration, password reset. Constraints: 24h session, bcrypt, rate limit 5 attempts. |

---

### dev

**Developer workflow tools: community scanning and technical decision-making.**

This plugin provides two powerful skills for developer research and decision-making.

#### Skills

**`/dev-scan`** - Scan developer communities for real opinions
- Searches Reddit (via Gemini CLI), Hacker News, Dev.to, and Lobsters in parallel
- Synthesizes consensus, controversies, and notable perspectives
- Great for understanding community sentiment before adopting a tool

**`/tech-decision`** - Deep technical decision analysis
- Multi-phase workflow with 4 specialized agents running in parallel
- Combines codebase analysis, docs research, community opinions, and AI perspectives
- Produces executive-summary-first reports with scored comparisons

**Trigger phrases:**
- "developer reactions to...", "what do devs think about..."
- "A vs B", "which library should I use", "기술 의사결정"

**How tech-decision works:**

```
Phase 1: Parallel Information Gathering
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│ codebase-       │ docs-           │ dev-scan        │ agent-council   │
│ explorer        │ researcher      │ (community)     │ (AI experts)    │
└────────┬────────┴────────┬────────┴────────┬────────┴────────┬────────┘
         └─────────────────┴─────────────────┴─────────────────┘
                                    │
Phase 2: Analysis & Synthesis       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        tradeoff-analyzer                                 │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       decision-synthesizer                               │
│                    (Executive Summary First)                             │
└─────────────────────────────────────────────────────────────────────────┘
```

```bash
# Examples
User: "React vs Vue for my new project?"
User: "Which state management library should I use?"
User: "Monolith vs microservices for our scale?"
```

---

### doubt

**Force Claude to double-check its response before delivering.**

When you include `!rv` anywhere in your prompt, Claude will pause before responding, re-validate its answer against potential errors, and only then deliver the response. Perfect for critical decisions or when you want extra confidence.

**Trigger:**
- Include `!rv` anywhere in your prompt

**How it works:**
1. `UserPromptSubmit` hook detects `!rv` keyword and sets a flag
2. `Stop` hook intercepts Claude's response before delivery
3. Claude re-validates the response for errors, hallucinations, or questionable claims
4. Only after verification does Claude deliver the final answer

**Why `!rv` instead of `!doubt`?**
The word "doubt" affects Claude's behavior - it starts doubting from the beginning. `!rv` (re-validate) is neutral.

```bash
# Example
User: "What's the time complexity of binary search? !rv"
# Claude will verify its answer before responding
```

---

### interactive-review

**Review Claude's plans and documents through a visual web interface.**

Instead of reading long markdown in the terminal, this plugin opens a browser-based UI where you can check/uncheck items, add comments, and submit structured feedback.

**Trigger phrases:**
- "/review"
- "review this plan"
- "let me check this"

**The flow:**
1. Claude generates a plan or document
2. A web UI opens automatically in your browser
3. Review each item with checkboxes and optional comments
4. Click Submit to send structured feedback back to Claude
5. Claude adjusts based on your approved/rejected items

---

### say-summary

![Demo](./assets/say-summary.gif)

**Hear Claude's responses spoken aloud (macOS only).**

This plugin uses a Stop hook to summarize Claude's response to a short headline and speaks it using macOS text-to-speech. Perfect for when you're coding and want audio feedback.

**Features:**
- Summarizes responses to 3-10 words using Claude Haiku
- Auto-detects Korean vs English
- Uses appropriate voice (Yuna for Korean, Samantha for English)
- Runs in background, doesn't block Claude Code

**Requirements:**
- macOS (uses the `say` command)
- Python 3.10+

---

### youtube-digest

![Demo](./assets/youtube-digest.jpeg)

**Summarize YouTube videos with transcripts, translations, and comprehension quizzes.**

Drop a YouTube URL and get a complete breakdown: summary, key insights, full Korean translation of the transcript, and a 3-stage quiz (9 questions total) to test your understanding.

**Trigger phrases:**
- "summarize this YouTube"
- "digest this video"
- YouTube URL

**What you get:**
1. **Summary** - 3-5 sentence overview with key points
2. **Insights** - Actionable takeaways and ideas
3. **Full transcript** - With Korean translation and timestamps
4. **3-stage quiz** - Basic, intermediate, and advanced questions
5. **Deep Research** (optional) - Web search to expand on the topic

**Output location:** `research/readings/youtube/YYYY-MM-DD-title.md`

---

### gmail

<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Gmail_icon_%282020%29.svg/1280px-Gmail_icon_%282020%29.svg.png" width="120" alt="Gmail">

**Manage multiple Gmail accounts from Claude Code.**

Read, search, send, and manage emails across multiple Google accounts with full Gmail API integration.

**Trigger phrases:**
- "check my email"
- "send an email to..."
- "search for emails from..."
- "reply to this email"
- "mark as read"

**Features:**
- Multi-account support via `accounts.yaml` (work, personal, etc.)
- Gmail search query syntax support
- Email sending with attachments and HTML
- Label and draft management
- **5-step email sending workflow** with context gathering, draft review, and test delivery
- Rate limiting and quota management
- Batch processing and local caching

**5-Step Email Workflow:**
1. **Context gathering** - Parallel Explore agents search recipient info and related projects
2. **Previous conversations** - Search recent emails to determine reply vs new thread
3. **Draft composition** - Create draft with user feedback
4. **Test send** - Send to your own email for verification
5. **Actual send** - Deliver to recipient

**Setup:**
1. Create Google Cloud project with Gmail API enabled
2. Run setup script for each account

```bash
# One-time setup per account
uv run python scripts/setup_auth.py --account work
uv run python scripts/setup_auth.py --account personal
```

Account metadata is stored in `accounts.yaml` for easy management.

---

### google-calendar

<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Google_Calendar_icon_%282020%29.svg/960px-Google_Calendar_icon_%282020%29.svg.png" width="120" alt="Google Calendar">

**Manage multiple Google Calendar accounts from Claude Code.**

Query, create, update, and delete events across multiple Google accounts (work, personal, etc.) with automatic conflict detection.

**Trigger phrases:**
- "show my schedule"
- "what's on my calendar"
- "create a meeting"
- "check for conflicts"

**Features:**
- Parallel querying across multiple accounts
- Conflict detection between accounts
- Full CRUD operations (create, read, update, delete)
- Pre-authenticated with refresh tokens (no repeated logins)

**Setup required:**
1. Create Google Cloud project with Calendar API
2. Run setup script for each account

```bash
# One-time setup per account
uv run python scripts/setup_auth.py --account work
uv run python scripts/setup_auth.py --account personal
```

---

### kakaotalk

![Demo](./assets/kakaotalk.gif)

**Send and read KakaoTalk messages from Claude Code on macOS.**

Uses macOS Accessibility API to control the KakaoTalk app. Send messages or read chat history using natural language.

**Trigger phrases:**
- "카톡 보내줘", "카카오톡 메시지"
- "~에게 메시지 보내줘"
- "채팅 읽어줘"
- "KakaoTalk message"

**Features:**
- Natural language message sending (with confirmation before send)
- Chat history retrieval
- Chat room listing
- Auto-signature "sent with claude code"

**Requirements:**
- macOS only
- KakaoTalk app must be running
- Accessibility permission required

```
# Examples (natural language)
"구봉한테 밥 먹었어? 보내줘"
"구봉이랑 대화 내역 보여줘"
```

---

### session-wrap

**Comprehensive session wrap-up and analysis toolkit.**

End your coding sessions with thorough analysis, and dive deep into session history for insights.

#### Skills

**`/wrap`** - Session wrap-up workflow
- 2-phase multi-agent pipeline for comprehensive session analysis
- Captures documentation needs, automation opportunities, learnings, and follow-ups
- `/wrap [commit message]` for quick commits

**`/history-insight`** - Session history analysis
- Analyze Claude Code session history for patterns and insights
- Search current project or all sessions
- Extract themes, decisions, and recurring topics

**`/session-analyzer`** - Post-hoc session validation
- Validate session behavior against SKILL.md specifications
- Check if agents, hooks, and tools executed correctly
- Generate detailed compliance reports

**How /wrap works (2-Phase Pipeline):**

```
Phase 1: Analysis (Parallel)
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ doc-updater  │ automation-  │ learning-    │ followup-    │
│              │ scout        │ extractor    │ suggester    │
└──────┬───────┴──────┬───────┴──────┬───────┴──────┬───────┘
       └──────────────┴──────────────┴──────────────┘
                            │
Phase 2: Validation         ▼
┌─────────────────────────────────────────────────────────────┐
│                    duplicate-checker                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                    User Selection
```

**Benefits:**
- Never forget to document important discoveries
- Identify patterns worth automating
- Create clear handoff points for future sessions
- Analyze past sessions for recurring patterns
- Validate skill implementations against specifications

---

## Contributing

Contributions welcome! Please open an issue or PR.

## License

MIT
