# team-assemble

Dynamically assemble expert agent teams for complex tasks using Claude Code's agent teams feature.

## What It Does

Instead of manually designing and coordinating multiple agents, team-assemble:

1. **Analyzes** your task and identifies relevant codebase areas
2. **Scouts** the codebase to understand what agents are needed
3. **Designs** an optimal team with the right roles and dependencies
4. **Executes** agents in parallel where possible
5. **Validates** results against acceptance criteria
6. **Cleans up** the team automatically

## Prerequisites

Agent teams are experimental and must be enabled first. Add to your `settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

See `skills/team-assemble/references/enable-agent-teams.md` for detailed setup instructions.

## Usage

Tell Claude what you need and ask it to assemble a team:

```
Assemble a team to refactor our authentication from session-based to JWT
```

```
Use team-assemble to evaluate caching strategies — Redis vs Memcached vs in-memory
```

```
Assemble a team to extract shared utilities from three microservices into a common library
```

The skill will guide you through approval gates before execution begins.

## How It Works

### 6-Phase Workflow

```
Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6
Task       Codebase   Integrate  Execute   Validate   Complete
Analysis   Scouts     & Confirm                       & Cleanup
```

### Model 3-Tier Strategy

Agents are assigned models based on their role:

| Model | Purpose | Examples |
|-------|---------|---------|
| opus | Strategy & judgment | Scouts, architects |
| sonnet | Standard execution | Implementers, QA, support |
| haiku | Research & writing | Researchers, editors |

### Key Features

- **Dynamic agent design** — no fixed catalog, agents are tailored to each task
- **Parallel execution** — independent agents run simultaneously
- **Acceptance criteria** — every team has measurable validation criteria
- **Verify/fix loop** — QA validates, support fixes (max 3 rounds)
- **Two approval gates** — user confirms scope (Phase 1) and team composition (Phase 3)

## Plugin Contents

```
team-assemble/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── team-assemble/
│       ├── SKILL.md                        # Main skill definition
│       └── references/
│           ├── agents.md                   # Agent example bank
│           ├── prompt-templates.md         # Prompt templates for all phases
│           ├── examples.md                 # Worked examples
│           └── enable-agent-teams.md       # Setup guide
└── README.md
```
