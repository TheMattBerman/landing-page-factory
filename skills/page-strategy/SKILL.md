---
name: page-strategy
description: "Normalize raw extract or manual brief into a page strategy artifact: mechanism, offer, audience, proof provenance, CTA, preservation plan, and review flags. Mandatory before copy or build."
metadata:
  openclaw:
    emoji: "🧭"
    user-invocable: true
    requires:
      env: []
---

# Page Strategy

This is the missing operator layer.

`site-extract` collects facts.
`page-strategy` decides what must be preserved, what can change, what proof is safe to use, and what page type should be built.

No strategy artifact, no page.

## Inputs

Required:
- `workspace/brand/extract.md` or manual brief

Optional:
- source screenshots
- product images
- existing brand profile
- operator notes about page goal

## Required output

Write both:
- `workspace/pages/[page-name]/strategy.md`
- `workspace/pages/[page-name]/strategy.json`

## Strategy schema

```markdown
# Page Strategy: [page-name]
Brand:
Page type:
Built:
Confidence:

## 1. Core decision
- Product / service:
- Offer:
- Audience:
- Awareness stage:
- CTA action:
- CTA destination:
- Conversion goal:

## 2. Mechanism map
- Primary buyer job:
- Primary pain:
- Failed alternatives:
- Unique mechanism:
- Why the mechanism works:
- What must be shown visually:
- What must be explained verbally:

## 3. Claims control
### Allowed claims
- [claim] — provenance class

### Forbidden claims
- [claim]

### Claims requiring proof near them
- [claim]

## 4. Proof plan
| Proof item | Class | Provenance | Where it should appear | Shippable? |
|---|---|---|---|---|

## 5. Preservation plan
### Trust cues to preserve
- 

### Visual conventions to preserve
- 

### Language to preserve
- exact phrases
- category terms buyers expect
- differentiators in source wording

### Deviations allowed
- what can be improved safely

## 6. Page routing
- Recommended page type:
- Hero structure:
- Proof structure:
- CTA strategy:
- Objection strategy:
- Required sections:
- Optional sections:

## 7. Visual requirements
- Visual preservation class: exact product / branded environment / concept support
- Screenshot handling: required / optional / forbidden
- Packaging fidelity needed? yes/no
- UI fidelity needed? yes/no
- Product silhouette fidelity needed? yes/no

## 8. Review flags
- compliance-sensitive claims
- thin proof
- missing CTA destination
- visual asset gaps
- any human approval needed
```

## Routing logic

Use these branches, not vibes.

### Physical product
Use product-led route when:
- product is visible and differentiated
- object form factor or materials matter
- mechanism can be staged visually

Hero must include:
- object clarity
- mechanism cue
- offer block
- trust cue above fold

### SaaS / app
Use screenshot-led route when:
- UI is central to trust or understanding
- claim depends on workflow visibility

Hero must include:
- real or preserved screenshot behavior
- outcome headline
- trust cue
- CTA

### Lead gen / service
Use friction-managed route when:
- user goal is booking, form fill, or consultation

Above fold must include:
- clear CTA destination
- friction reducer
- authority cue

### Regulated / sensitive niche
Use compliance-limited route when:
- health, supplements, finance, legal, or risk-heavy claims appear

Rules:
- strip unsupported claims
- downgrade certainty language
- raise review flag

## Stop / continue logic

Stop if:
- unique mechanism is blank
- CTA action is undefined
- source proof is too weak for proposed claims

Continue with downgrade if:
- proof is partial but enough for a softer page
- visuals are incomplete but can be handled with neutral support graphics

## Hand-off

Downstream order:
- `/brand-profile`
- `/page-copy`
- `/page-visuals`
- `/page-build`

Every downstream skill must read `strategy.json` first, then other artifacts.