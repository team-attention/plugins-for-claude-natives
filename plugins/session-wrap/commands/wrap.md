---
description: Session wrap-up - analyze session, suggest documentation updates, automation opportunities, and follow-up tasks
allowed-tools: Bash(git *), Read, Write, Edit, Glob, Grep, Task, AskUserQuestion
---

# Session Wrap-up (/wrap)

Wrap up the current session by analyzing work done and suggesting improvements.

## Prerequisites

Before starting, load the session-wrap skill for detailed workflow guidance.

## Quick Usage

- `/wrap` - Interactive session wrap-up (recommended)
- `/wrap [message]` - Quick commit with provided message

## Execution

Follow the workflow defined in the **session-wrap** skill:

1. Check git status
2. Phase 1: Run 4 analysis agents in parallel
3. Phase 2: Run validation agent
4. Integrate results and present options
5. Execute selected actions

Refer to `skills/session-wrap/SKILL.md` for detailed execution steps and agent configurations.
