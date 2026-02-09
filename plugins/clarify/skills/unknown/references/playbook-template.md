# Playbook Output Template

Complete template for the 4-quadrant playbook generated in Phase 6.

## File Naming

Save as: `{topic}-known-unknown.md` in a location appropriate to the project.

## Template

```markdown
# {Topic}: Known/Unknown Quadrant Analysis

> Based on {source document or conversation}.
> Designed under the constraint that "{key constraint from R1/R2}".

---

## Current State Diagnosis

- **{Finding 1}**: {confirmed fact from R1-R3}
- **{Finding 2}**: {confirmed fact}
- **What to stop doing**: {items user chose to cut}

---

## Quadrant Matrix

```
                    Known                          Unknown
         +---------------------------+---------------------------+
         |                           |                           |
         |   KK: Systematize         |   KU: Design Experiments  |
 Known   |   Resources: 60%          |   Resources: 25%          |
         |                           |                           |
         +---------------------------+---------------------------+
         |                           |                           |
         |   UK: Leverage            |   UU: Set Up Antennas     |
 Unknown |   Resources: 10%          |   Resources: 5%           |
         |                           |                           |
         +---------------------------+---------------------------+
```

---

## 1. Known Knowns: Systematize (60%)

> Confirmed working items. Turn into repeatable systems.

| # | Item | Evidence | Systemization Target |
|---|------|----------|---------------------|
| 1 | **{item}** | {how we know} | {what "systemized" looks like} |

---

## 2. Known Unknowns: Design Experiments (25%)

> Questions with no answer yet. Each gets an experiment.

### KU{N}. {Question}

**Diagnosis**: Why is this unknown?
- {root cause from R2}

**Experiment**:
| Item | Detail |
|------|--------|
| Format | {what to try} |
| Success criteria | {measurable outcome} |
| Deadline | {specific date} |
| Effort | {time/resource estimate} |

**Promotion condition**: {when this becomes a Known Known}
**Kill condition**: {when to abandon this and try something else}

*(Repeat for each prioritized KU)*

---

## 3. Unknown Knowns: Leverage (10%)

> Assets already owned but not utilized. Fastest wins.

| # | Hidden Asset | How to Use | Effort |
|---|-------------|-----------|--------|
| 1 | **{asset}** | {activation method} | Low/Med/High |

---

## 4. Unknown Unknowns: Set Up Antennas (5%)

> Cannot predict. Manage with detection speed + response speed.

| # | Risk/Opportunity | Detection Method | Response Principle |
|---|-----------------|-----------------|-------------------|
| 1 | **{scenario}** | {how to notice early} | {what to do} |

---

## Strategic Decision: What to Stop

| Item | Reason | Restart Condition |
|------|--------|------------------|
| **{item}** | {why stop} | {what would make it worth resuming} |

---

## Execution Roadmap

### Week 1-2
- [ ] {action item}
- [ ] {action item}

### Week 3-4
- [ ] {action item}

### Month 2
- [ ] {action item}
- [ ] Review: promote KUs to KK or kill

---

## Core Principles

1. **{Principle}**: {one-line explanation}
2. **{Principle}**: {one-line explanation}
3. **{Principle}**: {one-line explanation}
```

## Section Writing Guide

### Current State Diagnosis
Summarize only what was confirmed through R1-R3 questioning. Avoid restating the input document — focus on what the conversation revealed that wasn't obvious before.

### Known Knowns
Only include items with clear evidence. If the user said "I think so" without data, it's a KU not a KK.

### Known Unknowns
The most important section. Each KU must have:
- A root cause (why unknown)
- A minimum viable experiment (not a perfect plan)
- A measurable success criteria
- A promotion AND kill condition

### Unknown Knowns
Look for these in:
- Context files the user hasn't referenced
- Tools/skills already built but not used
- Past projects with reusable patterns
- Team members' unused expertise

### Unknown Unknowns
Keep this section short. The point is awareness, not prevention.
Focus on detection speed (how to notice early) and response capacity (having buffer time).

### What to Stop
This section is non-negotiable. Every analysis must include at least one item to stop or pause. Adding without subtracting is the most common failure mode.

### Core Principles
Derive from the conversation, not generic advice. Each principle should be a decision rule that resolves a specific tension discovered during questioning.
