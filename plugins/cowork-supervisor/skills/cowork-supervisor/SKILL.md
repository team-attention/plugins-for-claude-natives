---
name: cowork-supervisor
description: >
  Strategic orchestrator for multi-plugin coordination. Clarifies user intent through
  iterative questioning, discovers available plugin capabilities, creates execution plans,
  orchestrates multiple plugins, and aggregates results into coherent responses.
  Use when tasks span multiple domains (Finance, Legal, Marketing, Data, etc.).
license: MIT
compatibility: Designed for Claude Code
allowed-tools: Task AskUserQuestion Read Glob Grep
metadata:
  version: "1.0.0"
  category: "workflow"
  status: "active"
  updated: "2026-02-05"
  user-invocable: "true"
  tags: "supervisor, orchestrator, multi-plugin, coordination"
  argument-hint: "\"task description\""
---

# Cowork Supervisor

Strategic orchestrator that coordinates multiple Claude Code plugins to solve complex user requests.

## When to Use

- Task spans multiple domains (Finance + Legal + Marketing)
- Need data from multiple plugins combined
- Complex goal without specifying which plugins to use
- Cross-domain insights required

## How It Works

```
User Prompt
    |
    v
[1. Intent Clarifier] --> Clarified Intent Document
    |
    v
[2. Capability Discoverer] --> Capability Matrix
    |
    v
[3. Supervisor Planner] --> Execution Plan (User Approval)
    |
    v
[4. Orchestra] --> Execution Results
    |
    v
[5. Aggregator] --> Final Response
```

## Components

| Component | Purpose |
|-----------|---------|
| Intent Clarifier | Transform vague prompts into precise specifications |
| Capability Discoverer | Scan and catalog available plugin capabilities |
| Supervisor Planner | Create execution plans mapping tasks to plugins |
| Orchestra | Execute plans, dispatch to plugins, handle failures |
| Aggregator | Combine multi-plugin results into coherent response |

## User Interaction Points

1. **After Clarification**: Confirm understanding
2. **After Planning**: Approve execution plan
3. **On Error**: Choose recovery action
4. **After Completion**: Select next steps

## Example

**Input**: "Analyze competitor's financial health and IP risks"

**Flow**:
1. Clarifies: Which competitor? What aspects?
2. Discovers: Finance plugin, Legal plugin available
3. Plans: Parallel data gathering, then analysis
4. Orchestrates: Dispatches to Finance and Legal plugins
5. Aggregates: Combines results with cross-domain insights

**Output**: Comprehensive competitive analysis with source attribution

## Execution Directive

When activated:
1. Parse arguments for task description
2. Delegate to intent-clarifier for clarification
3. Delegate to capability-discoverer for plugin discovery
4. Delegate to supervisor-planner for plan creation
5. Present plan to user via AskUserQuestion
6. On approval, delegate to orchestra for execution
7. Delegate to aggregator for result synthesis
8. Present final response
9. Offer next steps via AskUserQuestion
