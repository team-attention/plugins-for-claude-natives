---
name: metamedium
description: This skill should be used when the user is building, planning, or strategizing and the key question is whether to optimize content (what) or change form (how/medium). Trigger on "내용 vs 형식", "content vs form", "metamedium", "형식을 바꿔볼까", "새로운 포맷", "관점 전환", "perspective shift", "다른 방법 없을까", "같은 방식이 안 먹혀", "diminishing returns". Applies Alan Kay's metamedium concept to surface form-level alternatives. For requirement clarification use vague; for strategy blind spots use unknown.
---

# Metamedium: Content vs Form Lens

Distinguish **content** (what is being said/built) from **form** (the medium/structure it's delivered through) to surface whether the real leverage is in optimizing content or inventing a new form. Based on Alan Kay's metamedium concept.

> "A change of perspective is worth 80 IQ points." — Alan Kay

## Core Concept

Most people only change **content** — what they say, write, or build. The real leverage comes from changing **form** — the medium, format, or structure itself.

| | Content (what) | Form (how/medium) |
|--|----------------|-------------------|
| Example | Writing a LinkedIn post | Building a tool that generates posts from client work |
| Example | Writing unit tests manually | Building a test generator from type signatures |
| Example | Giving a workshop | Inventing a format where attendees co-create artifacts |
| Leverage | Linear — each piece is one output | Exponential — each new form enables infinite content |

## When to Use

- Planning a project and unsure whether to optimize the output or the process
- Stuck optimizing content with diminishing returns
- Building something and want to check if form-level change would yield more leverage
- Evaluating whether "more of the same" or "something structurally different" is the right move

For requirement clarification, use the **vague** skill. For strategy blind spot analysis, use the **unknown** skill.

## Protocol

**ALWAYS use the AskUserQuestion tool** for the fork question in Phase 2 — never ask content/form choices in plain text.

### Phase 1: Identify and Label

Read the user's current work, plan, or task. Classify each component as content or form:

```
[CONTENT] Writing a blog post about AI consulting
[FORM]    Building a pipeline that turns consulting retros into blog posts
[CONTENT] Deploying a new API endpoint
[FORM]    Building a codegen that auto-generates endpoints from schemas
[CONTENT] Fixing a flaky test
[FORM]    Building a test infrastructure that prevents flaky tests by design
```

Present the labeling to the user as a brief diagnosis.

### Phase 2: Surface the Fork

Use AskUserQuestion to present the content/form choice:

```
questions:
  - question: "This is currently [CONTENT/FORM]-level work. Where should effort go?"
    header: "Level"
    options:
      - label: "Proceed with content"
        description: "Optimize within the current form — faster, lower risk"
      - label: "Explore form change"
        description: "What if the medium/structure itself changed? Higher leverage"
      - label: "Content now, note form"
        description: "Do the content work, but flag the form opportunity for later"
    multiSelect: false
```

### Phase 3: Branch

**If "Proceed with content"**: Acknowledge and proceed. Include a `Form Opportunity` note in the output for future reference.

**If "Explore form change"**: Generate 2-3 form alternatives. For each alternative:
- What the new form looks like concretely
- What new properties it would have (automatic, repeatable, scalable, composable)
- Minimum viable version to test the form

**If "Content now, note form"**: Proceed with content work. Append the form opportunity to the output.

### Output

Append to any deliverable or present standalone:

```markdown
## Content/Form Analysis

**Current work**: [description]
**Classification**: [CONTENT / FORM]

### Form Opportunity
| | Detail |
|---|--------|
| **Alternative form** | [what it would look like] |
| **New properties** | [what it enables that current form doesn't] |
| **Minimum test** | [smallest version to validate] |
| **Status** | [exploring / noted for later / not applicable] |
```

## The Metamedium Question

When stuck or when optimizing yields diminishing returns:

> **"What new form/medium could make this problem disappear?"**

Examples:
- Stuck writing more posts? → A format that turns client work into posts automatically
- Test coverage plateauing? → A tool that generates tests from type signatures
- Onboarding too slow? → A self-guided format where the codebase teaches itself

## Tetris Test

> Change the blocks. Then you realize the original blocks were mathematically calculated.

To truly understand a form, try to change it. The constraints discovered ARE the form's intelligence. Perspective shifts happen not by thinking harder, but by touching the form itself.

## Anti-Patterns

- Treating all work as content optimization when form change is available
- Building "better content" when the form is the bottleneck
- Assuming the current medium/format is fixed and only content can vary
- Confusing incremental content improvement with form invention

## Rules

1. **Always label**: Tag work as content or form
2. **Content is fine**: Not everything needs form change — but always note the option
3. **Form yields power**: New form = new medium = exponential leverage
4. **Code is metamedium**: The ability to code means the ability to change form
5. **Touch to understand**: Change the form to discover why it was designed that way

## Additional Resources

For Alan Kay's original ideas and source quotes, see `references/alan-kay-quotes.md`.
