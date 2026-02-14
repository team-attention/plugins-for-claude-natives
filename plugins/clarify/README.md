# Clarify

> Transform vague requirements into precise specifications through iterative questioning.

## How it Works

Clarify implements a 4-phase protocol for requirement refinement:

**Phase 1: Capture Original Requirement**
Records the user's requirement verbatim and identifies ambiguities, assumptions, and interpretation gaps.

**Phase 2: Iterative Clarification**
Uses structured questioning to resolve each ambiguity — specific over general, options over open-ended, one concern at a time, neutral framing.

**Phase 3: Before/After Comparison**
Presents the transformation showing: original vague requirement vs. clarified specification with Goal, Scope, Constraints, and Success Criteria.

**Phase 4: Save Option**
Offers to save the clarified requirement to `requirements/` directory in Markdown format.

## Setup

```bash
# Add the marketplace
/plugin marketplace add team-attention/plugins-for-claude-natives

# Install the plugin
/plugin install clarify@plugins-for-claude-natives
```

## Usage

```
"Clarify this requirement"
"Make this clearer"
"Refine requirements"
"/clarify"
```

## Ambiguity Categories

- **Scope** — what's included/excluded
- **Behavior** — edge cases, error scenarios
- **Interface** — interactions, users
- **Data** — inputs, outputs, formats
- **Constraints** — performance, compatibility
- **Priority** — must-have vs nice-to-have

## Project Structure

```
clarify/
├── .claude-plugin/
│   └── plugin.json     # Plugin metadata
└── skills/
    └── clarify/
        └── SKILL.md    # Skill definition and protocol
```

## License

MIT License
