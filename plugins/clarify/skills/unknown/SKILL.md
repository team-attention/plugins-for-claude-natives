---
name: unknown
description: This skill should be used when the user provides a strategy, plan, or decision document and wants to surface hidden assumptions and blind spots using the Known/Unknown 4-quadrant framework. Trigger on "known unknown", "4분면 분석", "blind spots", "뭘 놓치고 있지", "뭘 모르는지 모르겠어", "전략 점검", "전략 분석", "assumption check", "가정 점검", "quadrant analysis", "what am I missing". Strategy-level blind spot analysis with hypothesis-driven questioning. For requirement clarification use vague; for content-vs-form reframing use metamedium.
---

# Unknown: Surface Blind Spots with Known/Unknown Quadrants

Surface hidden assumptions and blind spots in any strategy, plan, or decision using the Known/Unknown quadrant framework and hypothesis-driven questioning.

## When to Use

- Strategy or planning documents that need scrutiny
- Decisions with unclear direction or hidden assumptions
- Any situation where "what we don't know" matters more than "what we do know"

For specific requirement clarification (feature requests, bug reports), use the **vague** skill. For content-vs-form reframing (optimizing within a form vs inventing a new form), use the **metamedium** skill.

## Core Principle: Hypothesis-as-Options

**ALWAYS use the AskUserQuestion tool** for every question in R1/R2/R3 — never ask questions in plain text. The structured format enforces hypothesis-as-options and limits choice fatigue.

Present hypotheses as options instead of open questions. The hypotheses ARE the analysis — by designing good options, 80% of the analytical work is done before the user even answers. The user's job is to confirm, correct, or surprise.

```
BAD:  "Why can't you do video content?"           ← open question, high load
GOOD: "Time / Skill gap / No guests / High bar"   ← pick one or more
```

- Each option IS a testable hypothesis about the user's situation
- Use multiSelect: true to catch compound causes
- "Other" is always available for out-of-frame answers

## 3-Round Depth Pattern

| Round | Purpose | Questions | Key trait |
|-------|---------|-----------|-----------|
| R1 | Validate draft quadrant | 3-4 | Broad, covers all quadrants |
| R2 | Drill into weak spots | 2-3 | Targeted, follows R1 answers |
| R3 | Nail execution details | 2-3 | Specific, optional |

**Critical**: Generate Round N questions from Round N-1 answers. Never use pre-prepared questions across rounds. Cap total at 7-10 questions.

## Protocol

### Phase 1: Intake

**File provided**: Read and extract goals, components, implicit assumptions, missing elements.

**Topic keyword only**: Start directly with R1 questions to establish scope. The draft in Phase 3 will be rougher but R1 corrects it.

### Phase 2: Context

Gather related context to find Unknown Knowns — assets the user may not realize they have:

- **Glob** for related files: CLAUDE.md, README, decision records, past analyses in the project
- **Read** project context: recent goals, team structure, active initiatives
- **Identify** underutilized assets: existing tools/skills not in use, past projects with reusable patterns, team expertise not leveraged

Items discovered here become UK candidates and options in R1 questions.

### Phase 3: Draft + R1 Questions

Generate an initial 4-quadrant classification. **The draft is intentionally rough** — R1 exists to correct it, not confirm it. Err on the side of classifying uncertain items as KU rather than KK.

Design R1 questions to test quadrant boundaries. **Batch all R1 questions into a single AskUserQuestion call** (max 4 questions):

| Target | Pattern | Example |
|--------|---------|---------|
| KK | "Is this really certain?" | "Primary revenue source?" (options) |
| KU | "Where's the weakest link?" | "Which flywheel connection is weakest?" |
| UK | "What exists but isn't used?" | Based on context findings |
| UU | "What's the biggest fear?" | Risk scenarios as options |

### Phase 4: Deepen + R2 Questions

Analyze R1 answers. Find the most uncertain area and drill in.

**R2 triggers**: compound answers (messy area), unexpected answers (draft wrong), "Other" selected (outside frame).

For detailed R2 question types, see `references/question-design.md`.

### Phase 5: Execute + R3 Questions (Optional)

After priorities are set, nail down execution details for top items. Skip if R2 already provides enough detail.

### Phase 6: Playbook Output

Generate a structured 4-quadrant playbook file. For the complete output template, see `references/playbook-template.md`.

**Output structure:**
```
# {Topic}: Known/Unknown Quadrant Analysis

## Current State Diagnosis
## Quadrant Matrix (ASCII with resource %)
## 1. Known Knowns: Systematize (60%)
## 2. Known Unknowns: Design Experiments (25%)
   - Each KU: Diagnosis → Experiment → Success Criteria → Deadline → Promotion Condition
## 3. Unknown Knowns: Leverage (10%)
## 4. Unknown Unknowns: Set Up Antennas (5%)
## Strategic Decision: What to Stop
## Execution Roadmap (week-by-week)
## Core Principles (3-5 decision criteria)
```

**Resource percentages (60/25/10/5) are defaults.** Adjust based on context — e.g., a startup exploring product-market fit may allocate 40% KU and 30% KK.

## Anti-Patterns

- Open questions ("What would you like to do?") — use hypothesis options
- 5+ options per question — causes choice fatigue
- Ignoring R1 answers when designing R2 — performative questioning
- Equal depth on all quadrants — wastes time, loses focus
- No "stop doing" section — adding without subtracting

## Example

**Input**: Growth strategy document

**R1**: Revenue source? → Workshops. Weakest link? → Biz→Knowledge. Blocker? → Skill gap + high bar (multiSelect). Biggest fear? → Execution scattered.

**R2** (driven by "execution scattered"): What to drop? → Product dev. Why no knowledge→content? → No process + no time + hard to abstract. Role clarity? → Unclear.

**R3**: Video format? → Screen recording. Retro blocker? → Don't know what to capture. What content resonated? → Raw discoveries.

**Key discovery**: Abstraction isn't needed — raw insights work better. Collapsed triple bottleneck into 15-minute pipeline.

## Rules

1. **Hypotheses, not questions**: Every option is a testable hypothesis
2. **Answers drive depth**: R2 from R1, R3 from R2
3. **7-10 questions max**: Beyond this is fatigue
4. **Stop > Start**: Always include "what to stop doing"
5. **Promote or kill**: Every KU gets a promotion condition and a kill condition
6. **Raw > Perfect**: Encourage minimum viable experiments, not perfect plans
7. **Draft is disposable**: The initial quadrant is meant to be corrected

## Additional Resources

### Reference Files

- **`references/question-design.md`** — Detailed question types for each round, trigger conditions, and AskUserQuestion formatting guide
- **`references/playbook-template.md`** — Complete output template with section-by-section guide
