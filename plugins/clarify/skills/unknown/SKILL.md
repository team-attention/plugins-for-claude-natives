---
name: unknown
description: This skill should be used when the user asks to "clarify unknowns", "known unknown", "4분면 분석", "quadrant analysis", "blind spots", "what am I missing", "surface assumptions", "strategy check", "뭘 놓치고 있지", "전략 점검", "분석해봐", or provides a strategy/plan/decision document that needs structured analysis to surface hidden assumptions and blind spots.
---

# Unknown: Surface Blind Spots with Known/Unknown Quadrants

Surface hidden assumptions and blind spots in any strategy, plan, or decision using the Known/Unknown quadrant framework and hypothesis-driven questioning.

## When to Use

- Strategy or planning documents that need scrutiny
- Decisions with unclear direction or hidden assumptions
- Any situation where "what we don't know" matters more than "what we do know"

For specific requirement clarification (feature requests, bug reports), use the **vague** skill instead.

## Core Principle: Hypothesis-as-Options

Present hypotheses as options instead of open questions. This reduces cognitive load and frames the user's thinking.

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

**Topic keyword only**: Start directly with R1 questions to establish scope.

### Phase 2: Context

Gather related context beyond the input: nearby files, decision records, project status, external data if needed.

### Phase 3: Draft + R1 Questions

Generate an initial 4-quadrant classification, then design R1 questions to test boundaries.

**R1 question design** — target each quadrant boundary:

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

## Additional Resources

### Reference Files

- **`references/question-design.md`** — Detailed question types for each round, trigger conditions, and AskUserQuestion formatting guide
- **`references/playbook-template.md`** — Complete output template with section-by-section guide
