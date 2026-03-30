---
name: brand-profile
description: "Build an evidence-backed brand profile from site extract and page strategy. Separates observed facts from synthesis so downstream skills preserve the brand instead of rewriting it."
metadata:
  openclaw:
    emoji: "🎨"
    user-invocable: true
    requires:
      env: []
---

# Brand Profile

This skill exists to normalize brand identity, not to write pretty summaries.

If the extract is weak, say the profile is low-confidence. Do not fake certainty.

## Required inputs

- `workspace/brand/extract.md`
- `workspace/pages/[page-name]/strategy.json` when available

## Outputs

Write:
- `workspace/brand/profile.md`
- `workspace/brand/palette.json`

## Required profile format

```markdown
# Brand Profile: [Brand]
Built:
Source confidence:

## Layer 1: Observed source evidence

### Exact phrases worth preserving
- 

### Exact phrases to avoid or not overuse
- 

### Claim inventory summary
- 

### Objection inventory summary
- 

### Mechanism language summary
- 

### Proof / trust summary
- 

### Visual motif summary
- 

### Page pattern summary
- 

## Layer 2: Synthesized operating profile

### Positioning
- one-line positioning
- key alternative it is beating
- buyer job

### Audience model
- primary buyer
- awareness stage
- sophistication
- pain priorities
- desire priorities

### Voice system
| Dimension | Position | Evidence |
|---|---|---|
| formal ↔ casual | | |
| reserved ↔ bold | | |
| technical ↔ accessible | | |
| practical ↔ aspirational | | |

### Language bank
- words they use
- category terms expected by buyers
- differentiator phrases
- words and tones to avoid

### Visual identity
- color system
- typography system
- photography / rendering style
- shape language
- spacing density
- trust-critical design conventions

### Confidence notes
- what is strongly grounded
- what is inferred
- what downstream should not overfit
```

## Palette contract

`palette.json` must include:
- colors with exact hex values
- font families and fallback stacks
- default radius range
- background / surface treatment
- confidence notes if values were inferred

## Rules

1. Evidence block first. Synthesis second.
2. Repeated source language is more valuable than abstract tone adjectives.
3. If strategy says certain trust cues or phrases must be preserved, keep them explicit.
4. Do not let anti-slop taste override category legitimacy.
5. Label uncertainty.

## Iteration behavior

If a profile exists:
- merge new evidence into the observed layer
- update synthesized layer only when new evidence justifies it
- highlight confidence shifts

## Hand-off

Used by:
- `page-copy`
- `page-visuals`
- `page-build`

But those skills must still read `strategy.json`. The profile is not a substitute for strategy.