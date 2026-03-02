# Prompt Templates

## 1. Codebase Scout Prompt

Template for scout agents in Phase 2.

```
## Mission

You are a codebase scout for the {area} area. Design expert agents to handle the task described below.

## Task
{user_task_description}

## Target Path
{target_path}

## Instructions

1. Read key files in this area to understand the current state:
   - CLAUDE.md, README.md (if present)
   - Directory structure (use Glob to explore)
   - Existing files/data related to the task

2. Propose agents needed for this task:
   - Use `references/agents.md` examples as inspiration (not mandatory)
   - Design entirely new agents when the task demands it
   - For each agent: name, role, specific tasks, reference files

3. Report any area-specific constraints or patterns to follow.

## Constraints
- Do NOT modify any files — exploration and analysis only
- Agent names must be kebab-case

## Output Format

### Current State
- {file structure and key findings summary}

### Proposed Agents
| Agent | Role | Tasks | Reference Files |
|-------|------|-------|-----------------|
| {name} | {role} | {specific task} | {file paths} |

### Notes
- {area-specific constraints, existing patterns, easy-to-miss details}
```

### Usage Example

```python
# Scout for the auth module
Agent(
    name="auth-scout",
    model="opus",
    subagent_type="general-purpose",
    prompt=scout_template.format(
        area="authentication",
        target_path="src/auth/",
        user_task_description="Refactor authentication to support OAuth2"
    )
)
```

When multiple areas are relevant, **launch scouts in parallel in a single message**:

```python
# Simultaneous execution
Agent(name="auth-scout", ...)
Agent(name="api-scout", ...)
```

---

## 2. Execution Agent Prompt

General prompt structure for execution agents in Phase 4.

### Structure (5 Sections)

```
## Context
{Project background and where this task fits in the overall work}
{Include preceding agent results if this task has dependencies}

## Goal
{Exactly what to achieve — clear and measurable}

## Reference Files
{List of relevant file paths identified by scouts}
- {path/to/file1} — {purpose}
- {path/to/file2} — {purpose}

## Constraints
- {What NOT to do}
- {Files/scope that must not be changed}
- {Rules to follow}

## Output Format
{Specific shape of the deliverable — markdown file, table, checklist, code, etc.}

## Team Info
- team_name: {team-name}
- task_id: {task-id}
- On completion: TaskUpdate(taskId: "{task-id}", status: "completed")
```

### Including Preceding Results

For agents with dependencies, inject the preceding agent's output directly:

```
## Context
You are part of the auth-refactor team.

### Preceding Results
{architect_result}

Based on the design above, implement the new authentication flow.
```

---

## 3. QA Prompt

Used for Phase 5 validation.

```
## Context
{Summary of overall team work}

## Acceptance Criteria
- [ ] AC-1: {criterion 1}
- [ ] AC-2: {criterion 2}
- [ ] AC-3: {criterion 3}

## Validation Target
{All Phase 4 execution results}

## Goal
Evaluate each acceptance criterion with evidence-based PASS/FAIL judgment.
- No PASS without evidence
- No subjective judgment — only objective evaluation against criteria
- No direct modifications (validation only)

## Output Format
| # | Criterion | Verdict | Evidence |
|---|-----------|---------|----------|
| 1 | {AC-1} | PASS/FAIL | {specific evidence} |

Overall: PASS / FAIL
If FAIL:
- Failure reason: {specific problem}
- Fix suggestion: {how to fix it}

## Team Info
- team_name: {team-name}
- task_id: {task-id}
- On completion: TaskUpdate(taskId: "{task-id}", status: "completed")
```

---

## 4. Support Prompt

Used when Phase 5 produces FAILs.

```
## Context
{Summary of team work}

## Failed Items
{qa's FAIL verdicts and fix suggestions}

## Goal
Fix only the FAIL items. Do NOT change anything beyond FAIL scope.

## Constraints
- Do NOT modify anything qa did not flag
- Do NOT break existing PASS items

## Output Format
| # | Failed Criterion | Fix Applied | Files Modified |
|---|-----------------|-------------|----------------|
State what needs to be re-validated.

## Team Info
- team_name: {team-name}
- task_id: {task-id}
- On completion: TaskUpdate(taskId: "{task-id}", status: "completed")
```

---

## Prompt Writing Tips

- **Be specific**: not "refactor the code" but "extract the validation logic from UserController into a ValidationService class"
- **Limit scope**: explicitly list which files/directories can be modified
- **Fix output format**: require structured output (tables, checklists) not free-form text
- **Include preceding results**: for dependent tasks, paste the previous agent's output into the prompt body
- **List reference files**: include relevant file paths from scout findings in the prompt
