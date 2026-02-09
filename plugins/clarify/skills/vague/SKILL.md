---
name: vague
description: This skill should be used when the user's request or requirement is ambiguous and needs iterative questioning to become actionable. Trigger on "clarify requirements", "refine requirements", "요구사항 명확히", "요구사항 정리", "뭘 원하는 건지", "make this clearer", "spec this out", "scope this", "/clarify". Turns vague inputs into concrete specs. For strategy blind spots use unknown; for content-vs-form reframing use metamedium.
---

# Vague: Requirement Clarification

Transform vague or ambiguous requirements into precise, actionable specifications through hypothesis-driven questioning. **ALWAYS use the AskUserQuestion tool** — never ask clarifying questions in plain text.

## When to Use

- Ambiguous feature requests ("add a login feature")
- Incomplete bug reports ("the export is broken")
- Underspecified tasks ("make the app faster")

For strategy/planning blind spot analysis, use the **unknown** skill. For content-vs-form reframing, use the **metamedium** skill.

## Core Principle: Hypotheses as Options

Present plausible interpretations as options instead of asking open questions. Each option is a testable hypothesis about what the user actually means.

```
BAD:  "What kind of login do you want?"           ← open question, high cognitive load
GOOD: "OAuth / Email+Password / SSO / Magic link" ← pick one, lower load
```

## Protocol

### Phase 1: Capture and Diagnose

Record the original requirement verbatim. Identify ambiguities:
- What is unclear or underspecified?
- What assumptions would need to be made?
- What decisions are left to interpretation?

### Phase 2: Iterative Clarification

Use AskUserQuestion to resolve ambiguities. **Batch up to 4 related questions per call.** Each option is a hypothesis about what the user means.

**Cap: 5-8 total questions.** Stop when all critical ambiguities are resolved, OR user indicates "good enough", OR cap reached.

**Example AskUserQuestion call:**
```
questions:
  - question: "Which authentication method should the login use?"
    header: "Auth method"
    options:
      - label: "Email + Password"
        description: "Traditional signup with email verification"
      - label: "OAuth (Google/GitHub)"
        description: "Delegated auth, no password management needed"
      - label: "Magic link"
        description: "Passwordless email-based login"
    multiSelect: false
  - question: "What should happen after registration?"
    header: "Post-signup"
    options:
      - label: "Immediate access"
        description: "User can use the app right away"
      - label: "Email verification first"
        description: "Must confirm email before access"
    multiSelect: false
```

### Phase 3: Before/After Summary

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

Ask whether to save the clarified requirement to a file. Default location: `requirements/` or project-appropriate directory.

## Ambiguity Categories

| Category | Example Hypotheses |
|----------|-------------------|
| **Scope** | All users / Admins only / Specific roles |
| **Behavior** | Fail silently / Show error / Auto-retry |
| **Interface** | REST API / GraphQL / CLI |
| **Data** | JSON / CSV / Both |
| **Constraints** | <100ms / <1s / No requirement |
| **Priority** | Must-have / Nice-to-have / Future |

## Rules

1. **Hypotheses, not open questions**: Every option is a plausible interpretation
2. **No assumptions**: Ask, don't assume
3. **Preserve intent**: Refine, don't redirect
4. **5-8 questions max**: Beyond this is fatigue
5. **Batch related questions**: Up to 4 per AskUserQuestion call
6. **Track changes**: Always show before/after
