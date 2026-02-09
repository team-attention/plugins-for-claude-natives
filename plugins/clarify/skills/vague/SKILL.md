---
name: vague
description: This skill should be used when the user asks to "clarify requirements", "refine requirements", "specify requirements", "what do I mean", "make this clearer", or when the user's request is ambiguous and needs iterative questioning to become actionable. Also trigger when user says "clarify", "/clarify", "ask me", or mentions unclear/vague requirements.
---

# Vague: Requirement Clarification

Transform vague or ambiguous requirements into precise, actionable specifications through iterative questioning with AskUserQuestion.

## When to Use

- Ambiguous feature requests ("add a login feature")
- Incomplete bug reports ("the export is broken")
- Underspecified tasks ("make the app faster")

For strategy/planning blind spot analysis, use the **unknown** skill instead.

## Protocol

### Phase 1: Capture Original Requirement

Record the original requirement verbatim. Identify ambiguities:
- What is unclear or underspecified?
- What assumptions would need to be made?
- What decisions are left to interpretation?

### Phase 2: Iterative Clarification

Use AskUserQuestion to resolve each ambiguity. Continue until ALL aspects are clear.

**Question Design Principles:**
- **Specific over general**: Ask about concrete details, not abstract preferences
- **Options over open-ended**: Provide 2-4 choices (recognition > recall)
- **One concern at a time**: Avoid bundling multiple questions
- **Neutral framing**: Present options without bias

**Loop:**
```
while ambiguities_remain:
    identify_most_critical_ambiguity()
    ask_clarifying_question()  # AskUserQuestion
    update_requirement_understanding()
    check_for_new_ambiguities()
```

### Phase 3: Before/After Comparison

Present the transformation:

```markdown
## Requirement Clarification Summary

### Before (Original)
"{original request verbatim}"

### After (Clarified)
**Goal**: [precise description]
**Scope**: [included and excluded]
**Constraints**: [limitations, preferences]
**Success Criteria**: [how to know when done]

**Decisions Made**:
| Question | Decision |
|----------|----------|
| [ambiguity 1] | [chosen option] |
```

### Phase 4: Save Option

Ask whether to save the clarified requirement to a file.
Default location: `requirements/` or project-appropriate directory.

## Ambiguity Categories

| Category | Example Questions |
|----------|------------------|
| **Scope** | What's included? What's explicitly out? |
| **Behavior** | Edge cases? Error scenarios? |
| **Interface** | Who/what interacts? How? |
| **Data** | Inputs? Outputs? Format? |
| **Constraints** | Performance? Compatibility? |
| **Priority** | Must-have vs nice-to-have? |

## Examples

### Vague Feature Request

**Original**: "Add a login feature"

**Clarifying questions (via AskUserQuestion)**:
1. Authentication method? → Username/Password
2. Registration included? → Yes, self-signup
3. Session duration? → 24 hours
4. Password requirements? → Min 8 chars, mixed case

**Clarified**:
- Goal: Add username/password login with self-registration
- Scope: Login, logout, registration, password reset
- Constraints: 24h session, bcrypt, rate limit 5 attempts
- Success: User can register, login, logout, reset password

### Bug Report

**Original**: "The export is broken"

**Clarifying questions**:
1. Which export? → CSV
2. What happens? → Empty file
3. When did it start? → After v2.1 update
4. Steps to reproduce? → Export any report

**Clarified**:
- Goal: Fix CSV export producing empty files
- Scope: CSV only, other formats work
- Constraint: Regression from v2.1
- Success: CSV contains correct data matching UI

## Rules

1. **No assumptions**: Ask, don't assume
2. **Preserve intent**: Refine, don't redirect
3. **Minimal questions**: Only ask what's needed
4. **Respect answers**: Accept user decisions
5. **Track changes**: Always show before/after
