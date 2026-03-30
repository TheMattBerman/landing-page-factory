---
name: page-copy
description: "Write mechanism-preserving, proof-disciplined landing page copy from strategy, brand profile, and extract language bank. Includes mandatory sharpness audit and claim control."
metadata:
  openclaw:
    emoji: "✍️"
    user-invocable: true
    requires:
      env: []
---

# Page Copy

Good landing page copy is not generic persuasion sludge. It is a controlled translation of the mechanism, offer, proof, and objection map into page sections.

If strategy is missing, stop.

## Required inputs

1. `workspace/pages/[page-name]/strategy.json`
2. `workspace/brand/profile.md`
3. `workspace/brand/extract.md`

## Pre-write control block

Before drafting, print and honor:
- Offer
- Unique mechanism
- Allowed claims
- Forbidden claims
- Available proof
- Priority objections
- CTA action
- CTA destination

If any are missing, downgrade or stop.

## Copy rules

1. Mechanism first. A good-looking page that weakens the mechanism is bad copy.
2. Use extracted language where it is strongest.
3. Every section has one job.
4. Do not use unearned certainty.
5. Do not upgrade missing proof into verified proof.
6. Ban empty phrases unless directly quoted from source.

## Hard ban list

Cut these unless there is direct source evidence and a damn good reason:
- elevate
- seamless
- unlock
- next-gen
- cutting-edge
- revolutionize
- transform your business
- premium solution
- game-changer
- innovative platform

## Required section order

The exact layout can vary, but the copy artifact must include:
- strategy snapshot
- hero
- problem / failed alternative
- mechanism / solution
- proof
- objections
- CTA close
- metadata
- sharpness audit

## Required output format

```markdown
# [Page Name] — Copy
Brand:
Generated:
Page type:
Awareness stage:
CTA:

## STRATEGY SNAPSHOT
- Offer:
- Unique mechanism:
- Allowed claims:
- Forbidden claims:
- Proof available:
- Priority objections:

## HERO
### Headline options
1. 
2. 
3. 
Recommended:
Reason:

### Subheadline

### CTA

### Above-fold trust cue

## PROBLEM / FAILED ALTERNATIVE

## MECHANISM / SOLUTION
- explain why this works
- tie benefits directly to failed alternatives

## PROOF
| Element | Copy | Provenance | Shippable? |
|---|---|---|---|

## OBJECTIONS
Q:
A:

## FINAL CTA

## PAGE METADATA
- SEO title
- Meta description
- OG title
- OG description

## SHARPNESS AUDIT
| Dimension | Score /10 | Pass threshold | Notes |
|---|---:|---:|---|
| mechanism clarity | | 8 | |
| specificity | | 8 | |
| proof density | | 7 | |
| objection coverage | | 7 | |
| phrase originality | | 7 | |
| section discipline | | 8 | |
| CTA clarity | | 8 | |

Overall: pass / fail
Required cuts:
- 
```

## Reduction pass

After draft one, force a cut pass:
- remove at least 20 percent of lines that are redundant, generic, or self-congratulatory
- keep or improve clarity while shortening

If the copy is already extremely lean, say so and skip with justification.

## Proof discipline

In the PROOF section, every item must show provenance:
- `verified_source`
- `derived_source`
- `placeholder_draft`
- `missing`

Anything not verified or derived must be flagged as non-shippable.

## Section guidance

### Hero
Choose the angle by awareness stage and strategy.
Do not lead with vague outcomes if the mechanism is the reason buyers convert.

### Problem
Use buyer pain and failed alternatives from extract or strategy.
No melodrama.

### Mechanism / solution
This is mandatory. If the page cannot explain why the product works, the page is not ready.

### Proof
Best proof handles objections indirectly.
Use specificity.

### Objections
Answer the real blockers, not fake FAQs nobody asked.

### CTA close
Restate the offer and reduce friction.
Only use urgency when it is real.

## Stop / continue logic

Stop if:
- strategy is missing
- unique mechanism is blank
- most proof items are missing but copy depends on them

Continue with downgrade if:
- proof is limited but soft claims still work
- brand voice confidence is medium or low

## Eval Reference

For scoring criteria and pass thresholds, see `references/eval-rubric.md` at the repo root.

## Hand-off

After copy, run `page-visuals` and `page-build`.