# Agent Example Bank

Reference examples for designing agents. Scouts use these as inspiration, not as a fixed catalog.

> This is an **example bank**, not a mandatory catalog. Scouts should reference these but can design entirely new agents optimized for each task. Names, roles, and tasks should all be tailored to the work at hand.

## General Policy

- **subagent_type**: `general-purpose`
- **mode**: `bypassPermissions`

### Model 3-Tier

Choose based on role purpose:

| Model | When to Use | Example Roles |
|-------|-------------|---------------|
| `opus` | Strategy/judgment required | scouts, complex execution agents |
| `sonnet` | Standard execution/validation | workers, qa, support |
| `haiku` | Information gathering/writing | researcher, editor, simple writer |

**Decision rule**: "Does it need to make new judgments?" → opus. "Does it execute against given criteria?" → sonnet. "Does it find information or write text?" → haiku.

---

## Software Engineering Examples

| Agent | Role | Use Case |
|-------|------|----------|
| architect | System design, API design, module structure | "Design the auth refactor" |
| implementer | Write production code based on a design | "Implement the new auth flow" |
| test-writer | Write unit/integration/e2e tests | "Add test coverage for auth" |
| refactorer | Improve code structure without changing behavior | "Clean up legacy patterns" |
| migrator | Database/schema/API migration scripts | "Migrate from v1 to v2 schema" |
| reviewer | Code review with specific focus area | "Review for security issues" |
| debugger | Investigate and fix specific bugs | "Find root cause of timeout" |
| docs-writer | Write or update documentation | "Update API docs for new endpoints" |

## Research & Analysis Examples

| Agent | Role | Use Case |
|-------|------|----------|
| researcher | Investigate topics, gather information | "Research auth library options" |
| analyst | Analyze data, derive insights | "Analyze error patterns in logs" |
| benchmarker | Performance testing and comparison | "Benchmark three caching strategies" |
| competitor-analyst | Compare competing solutions | "Compare our API with competitors" |

## Content & Communication Examples

| Agent | Role | Use Case |
|-------|------|----------|
| writer | Draft documents, reports, emails | "Write the RFC for the new feature" |
| editor | Refine and polish written content | "Edit the blog post for clarity" |
| strategist | Plan content or communication strategy | "Plan the launch announcement" |

## Project Management Examples

| Agent | Role | Use Case |
|-------|------|----------|
| product-manager | PRD writing, backlog management, requirements | "Write the PRD for notifications" |
| project-coordinator | Timeline, milestones, stakeholder comms | "Create the migration timeline" |
| ux-designer | Wireframes, user journeys, UI specs | "Design the onboarding flow" |

---

## Common Agents (Always Included)

Every team must include these roles:

| Agent | Role | Notes |
|-------|------|-------|
| qa | Evidence-based PASS/FAIL evaluation against acceptance criteria | Phase 5 validation only |
| support | Fix FAIL items from qa, verify/fix loop | Deployed only when Phase 5 has FAILs |

### qa Behavior Rules

- No PASS without evidence
- No subjective judgment — only objective evaluation against acceptance criteria
- No direct code modifications (validation only)

### support Behavior Rules

- Fix only FAIL items — no out-of-scope changes
- Do not modify anything qa did not flag

---

## Agent Design Checklist

When a scout designs a new agent:

1. **Name**: kebab-case, role should be immediately obvious
2. **Role**: one sentence defining the core responsibility
3. **Tasks**: specific deliverables for this particular project
4. **Reference files**: file/directory paths the agent needs to read
5. **Constraints**: what the agent must NOT do (scope guard)
6. **Dependencies**: which agent results must come first
