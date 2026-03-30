---
name: page-visuals
description: "Plan and generate visuals by preservation class: exact product, branded environment, or concept support. Uses strategy-driven shot selection and visual QA instead of generic vibe prompting."
metadata:
  openclaw:
    emoji: "📸"
    user-invocable: true
    requires:
      env: []
---

# Page Visuals

The job is not "make pretty images." The job is to support conversion without visually lying about the thing being sold.

If the product, packaging, UI, or materials need precision, route accordingly.

## Required inputs

1. `workspace/pages/[page-name]/strategy.json`
2. `workspace/brand/profile.md`
3. `workspace/brand/palette.json`
4. `workspace/pages/[page-name]/copy.md`
5. any operator-provided product refs, packaging refs, screenshots, or image assets

## Preservation classes

Every planned visual must be classified before prompting.

### 1. Exact product preservation
Use when the product’s shape, materials, packaging, UI, or industrial design matter to trust or understanding.

Requirements:
- preserve silhouette
- preserve proportions
- preserve material look
- preserve packaging where relevant
- preserve UI/screen content where relevant
- use references whenever available

### 2. Branded environment preservation
Use when the product can sit in a brand-specific context but does not require perfect object fidelity.

Requirements:
- match palette and audience world
- keep brand mood and category realism
- avoid stock-photo staging

### 3. Concept-support visual
Use when the image is explanatory, atmospheric, or background support rather than trust-critical product proof.

Requirements:
- support the mechanism or section job
- stay subordinate to copy
- do not introduce fake product details

## Shot prioritization hierarchy

Generate in this order:
1. proof / mechanism visual
2. product clarity visual
3. lifestyle aspiration visual
4. decorative support visual

If time or budget is limited, drop 4 first.

## Required shot plan output

Write `workspace/pages/[page-name]/visuals/index.md` with:

```markdown
# Visual Plan: [page-name]
Generated:

| Shot | Section | Preservation class | Purpose | Required refs | Status |
|---|---|---|---|---|---|
| hero-1 | hero | exact product / branded environment / concept support | | | planned |
```

## Prompting rules

Always include:
- intended section and job
- preservation class
- composition requirement
- palette direction
- mood / lighting
- fidelity constraints
- explicit exclusions

### For exact product preservation
Prompt must state:
- preserve object silhouette and proportions
- preserve material finish
- preserve packaging/UI only from reference
- no invented text or altered brand marks

### For branded environment
Prompt must state:
- audience context
- authentic use moment
- palette integration through environment, props, wardrobe, or lighting
- no canned stock-photo poses

### For concept-support
Prompt must state:
- section job
- minimalism / abstraction level
- no fake claim-bearing details

## Screenshot / UI handling

If strategy marks screenshot handling as required:
- preserve screenshots or UI references
- do not freehand fake UI precision
- if no real UI assets exist, raise a flag and downgrade the shot plan

## Visual QA rubric

Every generated image must be scored:

| Dimension | Score /10 | Pass threshold |
|---|---:|---:|
| section-fit | | 8 |
| palette fidelity | | 8 |
| silhouette / geometry fidelity | | 8 when applicable |
| material fidelity | | 8 when applicable |
| packaging / UI fidelity | | 8 when applicable |
| composition clarity | | 8 |
| artifact absence | | 9 |
| text artifact absence | | 10 |

Reject and regenerate if any required dimension fails.

## Failure logic

If exact product fidelity is failing repeatedly:
- stop using loose brand-vibe prompts
- require tighter references
- downgrade to preserved photography or operator-provided asset if available
- never fake exactness because the model is struggling

## Hand-off

After visuals are approved, run `page-build`.