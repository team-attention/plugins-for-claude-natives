---
name: supervise
description: >
  Orchestrate multiple Cowork plugins to solve complex tasks. Clarifies intent,
  discovers capabilities, plans execution, and coordinates plugins.
  Usage: /supervise "task description"
allowed-tools: Task AskUserQuestion Read Glob Grep
---

# /supervise Command

Strategic orchestrator for multi-plugin coordination in Cowork.

## Usage

```
/supervise "Analyze competitor's financial health and IP portfolio"
/supervise "Create marketing campaign with budget analysis and legal review"
/supervise "Generate quarterly report combining sales, finance, and customer data"
```

## What It Does

1. **Clarifies** your request through targeted questions
2. **Discovers** available plugins and their capabilities
3. **Plans** execution strategy (parallel/sequential tasks)
4. **Coordinates** multiple plugins to execute the plan
5. **Aggregates** results into a unified response

## When to Use

- Tasks spanning multiple business domains
- Complex analysis requiring multiple data sources
- Cross-functional workflows
- When unsure which plugins to use

## Workflow

```
Your Request
    |
    v
Intent Clarification (questions to understand your needs)
    |
    v
Capability Discovery (find matching plugins)
    |
    v
Execution Planning (you approve before execution)
    |
    v
Multi-Plugin Orchestration (parallel when possible)
    |
    v
Result Aggregation (unified response with sources)
```

## Example Session

**You**: `/supervise "Evaluate acquisition target Acme Corp"`

**Supervisor**: "I'll help evaluate Acme Corp as an acquisition target. Let me clarify:

What aspects should I analyze?
1. Financial health only
2. Legal/IP risks only
3. Both financial and legal
4. Comprehensive (financial, legal, market position)"

**You**: Select option 3

**Supervisor**: Creates and presents execution plan...

**You**: Approve plan

**Supervisor**: Executes Finance plugin + Legal plugin in parallel, then aggregates results into comprehensive evaluation report.

## Supported Plugins

The supervisor can coordinate any installed Cowork plugins:
- Finance (financial analysis, budgeting)
- Legal (contracts, IP, compliance)
- Marketing (campaigns, market analysis)
- Sales (pipeline, forecasting)
- Data (data gathering, connectors)
- Customer Support (ticket analysis)
- And any other installed plugins

## Options

No command-line options. All configuration happens through the interactive clarification process.

## Execution

This command invokes the cowork-supervisor skill which delegates to specialized agents:
- intent-clarifier: Understands your request
- capability-discoverer: Finds available plugins
- supervisor-planner: Creates execution plan
- orchestra: Coordinates plugin execution
- aggregator: Combines results
