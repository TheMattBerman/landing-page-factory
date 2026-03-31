---
name: page-qa
description: "Final landing-page QA pass against strategy, proof provenance, mechanism clarity, trust preservation, accessibility, and anti-slop. Gates whether a page is shippable or draft-only."
metadata:
  openclaw:
    emoji: "✅"
    user-invocable: true
    requires:
      env: []
---

# Page QA

This is the final gate. It exists because good-looking pages can still be strategically wrong, untrustworthy, or impossible to ship.

## Required inputs

- `workspace/pages/[page-name]/strategy.json`
- `workspace/pages/[page-name]/copy.md`
- `workspace/pages/[page-name]/index.html`
- `workspace/pages/[page-name]/meta.json`
- `workspace/pages/[page-name]/visuals/index.md`
- `references/anti-slop.md`

## QA dimensions

Score each 1-10 unless pass/fail is more appropriate.

### 1. Mechanism preservation
- is the unique mechanism visible and understandable?
- does the page explain why this works?
- did aesthetics overpower explanation?

### 2. Proof discipline
- are all stats, testimonials, logos, guarantees, and claims provenance-tagged?
- is anything non-shippable still presented as real?

### 3. Trust cue preservation
- were critical trust conventions preserved?
- were category-legitimacy cues kept intact?

### 4. Copy sharpness
- specificity
- fluff control
- objection coverage
- CTA clarity

### 5. Visual fidelity
- correct preservation class use
- no fake precision where exactness was required
- no obvious artifacts

### 6. Build quality
- responsive structure
- contrast
- semantics
- focus states
- alt text

### 7. Anti-slop compliance
- no banned patterns
- anti-slop used without overriding brand fidelity

## Output format

Write `workspace/pages/[page-name]/qa.md`:

```markdown
# QA Report: [page-name]
Generated:

| Dimension | Score | Threshold | Result | Notes |
|---|---:|---:|---|---|
| mechanism preservation | | 8 | pass/fail | |
| proof discipline | | 9 | pass/fail | |
| trust cue preservation | | 8 | pass/fail | |
| copy sharpness | | 8 | pass/fail | |
| visual fidelity | | 8 | pass/fail | |
| build quality | | 8 | pass/fail | |
| anti-slop compliance | | 8 | pass/fail | |

## Hard fails
- 

## Draft-only flags
- 

## Required fixes before ship
1. 
2. 
3. 

## Verdict
- shippable
- draft only
- blocked
```

## Eval Reference

For the full scoring criteria, pass thresholds, ranking weights, and verdict logic, see `references/eval-rubric.md` (bundled with this skill).

## Verdict logic

Blocked if:
- proof is invented or untraceable in a way that affects conversion claims
- mechanism is unclear
- CTA path is broken
- critical accessibility or rendering issues exist

Draft only if:
- structure is good but proof or asset gaps remain
- some visuals are placeholders
- compliance review is still required

Shippable only if all hard thresholds pass.
