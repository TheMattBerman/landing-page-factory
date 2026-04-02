---
name: page-build
description: "Build a deployable landing page from strategy, copy, visuals, and brand profile using category-aware routing, preservation hierarchy, and explicit QA. Single-file HTML output."
metadata:
  openclaw:
    emoji: "🏗️"
    user-invocable: true
    requires:
      env: []
---

# Page Build

Build quality comes after strategic fidelity, not before it.

This stage assembles the page while preserving what matters for trust and conversion.

## Required inputs

1. `workspace/pages/[page-name]/strategy.json`
2. `workspace/brand/profile.md`
3. `workspace/brand/palette.json`
4. `workspace/pages/[page-name]/copy.md`
5. `workspace/pages/[page-name]/visuals/`
6. `references/anti-slop.md` (bundled with this skill)

If strategy is missing, stop.

If `workspace/pages/[page-name]/visuals/manifest.json` exists, use it as the canonical machine-readable visual source.
Do not ignore provider metadata when it affects trust, fidelity, or fallback history.

## Preservation hierarchy

Apply in this order:
1. preserve trust-critical category conventions
2. preserve mechanism communication needs
3. preserve brand visual identity
4. improve layout rhythm and interaction quality
5. apply anti-slop taste improvements only where they do not distort 1-4

Anti-slop is a quality filter, not a redesign license.

## Pre-build checklist

Before generating HTML, confirm:
- page type confirmed
- conversion mechanism confirmed
- proof inventory loaded
- trust cues selected
- visual manifest resolved into build-ready image paths
- required category conventions preserved
- CTA destination known
- layout choice justified in one line

If any are false, stop or downgrade.

## Routing logic

### Physical product route
Use when strategy page type is product-led.

Above fold must include:
- clear product or mechanism visual
- offer headline
- CTA
- trust cue

### SaaS / app route
Above fold must include:
- preserved screenshot or UI treatment if required
- outcome headline
- trust cue
- CTA

### Lead capture route
Above fold must include either:
- form + friction reducer
or
- clear CTA into a known destination

### Authority / service route
Must include:
- authority cue above fold
- proof section early
- objection handling around trust and fit

### Regulated route
Must include:
- downgraded certainty when proof is partial
- compliance review flag in metadata

## Design rules

- single HTML file
- responsive at minimum 768px and 1024px breakpoints
- semantic HTML
- visible focus states
- alt text on all images
- no builder attribution unless explicitly requested
- no imported taste pattern that overrides source trust cues

## Anti-slop usage

Load `references/anti-slop.md` and apply it after the preservation hierarchy, not before.

## Post-build QA table

Write this into `workspace/pages/[page-name]/qa.md` and summarize in `meta.json`:

| Check | Pass? | Notes |
|---|---|---|
| mechanism visible above fold | | |
| primary proof visible above fold | | |
| CTA above fold | | |
| trust cue above fold | | |
| no invented proof | | |
| no banned slop patterns | | |
| mobile collapse checked | | |
| contrast checked | | |
| alt text present | | |
| category convention preserved | | |

## Metadata contract

`meta.json` must include:
- brand
- page
- page_type
- mechanism_type
- template_route
- CTA_destination
- proof_items with provenance summary
- risk_reversal_present
- compliance_flags
- review_flags
- preserved_elements
- deviations_from_source
- images_used
- sections_present
- build_confidence

When a visual manifest exists, also include:
- `hero_image`
- `image_provider_policy`
- `images_used` as structured objects, not only bare filenames
- provider and fallback context when relevant to review or QA

## Build helper

Use `scripts/resolve-visual-assets.py --page-name [page-name]` to convert `visuals/manifest.json`
into build-ready image metadata for HTML and `meta.json`.

Then use `scripts/prepare-build-meta.py --page-name [page-name] --resolved-assets [file]`
to merge those resolved assets into `meta.json` with deterministic selection fields:
- `hero_image`
- `mechanism_image`
- `lifestyle_image`
- `og_image`
- `image_slots.hero`
- `image_slots.mechanism`
- `image_slots.lifestyle`
- `image_slots.og`

Then use `skills/page-build/scripts/html-image-context.py --meta workspace/pages/[page-name]/meta.json`
to emit literal HTML-ready values such as:
- `hero_img_src`
- `hero_img_alt`
- `mechanism_img_src`
- `mechanism_img_alt`
- `lifestyle_img_src`
- `lifestyle_img_alt`
- `og_image_path`

Minimal executable builder:
- `skills/page-build/scripts/build-page.py --page-name [page-name]`
  This consumes `strategy.json`, `meta.json`, and `html-image-context.json` and writes a real `index.html` scaffold.

Use the skill-local scripts as the primary interface for Cowork or any agent runtime that only uploads the skill folder.
The repo-root `/scripts` copies are local development conveniences, not a packaging requirement.

## Eval Reference

For scoring criteria and pass thresholds, see `skills/page-qa/references/eval-rubric.md`.
For anti-slop patterns, see `references/anti-slop.md` (bundled with this skill).

## Stop / continue logic

Stop if:
- CTA destination is unknown for a lead action page
- page depends on proof that is missing
- required trust cues cannot be supported

Continue with downgrade if:
- visual assets are partial but neutral support layout still works
- proof is light but the page is reframed to softer claims

## Output

Write:
- `workspace/pages/[page-name]/index.html`
- `workspace/pages/[page-name]/meta.json`
- `workspace/pages/[page-name]/qa.md`

A build without QA output is incomplete.
