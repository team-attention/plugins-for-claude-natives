# Question Design Guide

Detailed patterns for designing hypothesis-driven questions across the 3-round depth pattern.

## AskUserQuestion Formatting

```
question: "Clear, specific question ending with ?"
header: "Short label (max 12 chars)"
options:
  - label: "Option A"
    description: "Why this matters or what it implies"
  - label: "Option B"
    description: "Why this matters or what it implies"
multiSelect: true  # when compound causes are likely
```

**Rules:**
- 3-4 options per question (never 5+)
- description explains implications, not just restates label
- multiSelect for cause/blocker questions, single for priority/choice questions

## R1 Questions: Validate the Draft

Design one question per quadrant boundary. Goal: confirm or correct the initial classification.

| Quadrant | Question Pattern | Example |
|----------|-----------------|---------|
| **KK** | "What's the confirmed reality?" | "Current revenue source?" with options per hypothesis |
| **KU** | "Where's the weakest link?" | "Which connection in your process is weakest?" |
| **UK** | "What assets exist but aren't used?" | "Which of these do you have but don't leverage?" |
| **UU** | "What's the scariest scenario?" | "Most feared outcome?" with risk scenarios |

**Tip**: If context exploration reveals surprising assets, surface them in the UK question as options.

## R2 Questions: Deepen the Weak Spots

Triggered by R1 answers. Focus on the 1-2 most uncertain areas.

### When to Use Each Type

| R2 Type | Trigger | Example |
|---------|---------|---------|
| **Root cause** | KU has unclear "why" | "Core reason video content isn't happening?" |
| **Feasibility** | Proposed solution seems hard | "Is a 30-min weekly retro realistic? What's blocked it?" |
| **Priority** | Multiple items compete | "Pick top 3 from these 6 Known Unknowns" |
| **Hidden constraint** | Suspected unstated limit | "Tried converting consulting into content before? Result?" |
| **Drop candidate** | "Execution scattered" emerged | "Which of these can be stopped or paused?" |

### Reading R1 Answers

| R1 Signal | R2 Strategy |
|-----------|-------------|
| Compound answer (multiSelect) | That area is complex — break it apart with root cause question |
| Unexpected answer | Draft was wrong — revise quadrant, probe deeper |
| "Other" selected | User sees outside the frame — open exploration |
| Strong conviction | Area is likely KK — validate with evidence question, then move on |

## R3 Questions: Execution Details

Only for the prioritized top items. Skip if R2 provides enough.

| R3 Type | When | Example |
|---------|------|---------|
| Tool/channel | Multiple ways to execute | "Publish via: YouTube Live / Local recording / Podcast?" |
| Pattern ID | Need to design a template | "What type of insight do you find most often in projects?" |
| Past experience | Checking if this was tried before | "Have you tried turning this into content? What worked?" |
| Success signal | Defining "done" | "What response tells you this format is worth repeating?" |

## Common Mistakes

### Asking the same question twice in different words
R1: "What's your biggest challenge?" R2: "What's hardest right now?"
Fix: R2 must drill INTO the R1 answer, not re-ask it.

### Options that aren't real hypotheses
"Option A: Good" "Option B: Bad" "Option C: Maybe"
Fix: Each option should represent a distinct, plausible situation.

### Skipping multiSelect when causes are compound
"Why can't you do video?" with single-select misses "skill gap AND high standards"
Fix: Default to multiSelect for "why/blocker" questions.

### Going past 10 total questions
Fatigue kills quality. If R2 answers are clear, skip R3 entirely.
