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

## Provider policy

Use Page Factory brand artifacts as the source of truth.

- `workspace/brand/extract.md` and `workspace/brand/profile.md` define the canonical brand understanding
- provider-side brand onboarding is support context for image generation, not a substitute for extraction or profiling
- preferred provider order: Bloom first pass, Nano Banana fallback, then manual/operator assets when fidelity is trust-critical

Provider selection is mandatory.

If Bloom is configured or expected for the run, you must check Bloom first.
Do not silently substitute Cowork-native image generation, generic built-in image tools, or ad hoc image prompting when Bloom is the intended provider.

If Bloom is not configured, blocked, or cannot be reached:
1. say that explicitly
2. ask the operator whether to:
   - provide/configure Bloom
   - use Nano Banana fallback
   - supply manual/operator assets
3. do not silently continue with a weaker provider on a trust-critical run

If Nano Banana is the fallback path, confirm that the operator has provided the required adapter/command or API-backed workflow.
Do not assume Nano Banana exists just because the name appears in docs.

### Bloom-specific guidance

When Bloom is available:
- check whether the brand already exists in Bloom
- if not, onboard the brand from the source URL
- if Bloom brand context is weak or incomplete, fill it using the repo's extracted brand facts, profile, and palette
- upload product, packaging, or UI refs before generating exact-product shots
- use Bloom edits/resizes when the base composition is strong and the change request is narrow

Fallback to Nano Banana when:
- Bloom is unavailable or not configured
- Bloom onboarding fails repeatedly
- Bloom has insufficient credits
- a required image fails the visual QA rubric after reasonable retries

Before switching to Nano Banana, explicitly note why Bloom was not used:
- unavailable
- not configured
- blocked by runtime
- QA failure after retries
- insufficient credits

## Provider helper

Use the skill-local image provider entrypoint to run actual image generation with provider fallback:

```bash
bash skills/page-visuals/scripts/image-provider.sh \
  --page-name [page-name] \
  --shot-id [shot-id] \
  --prompt "[prompt]" \
  --preservation-class [exact_product|branded_environment|concept_support]
```

Use `skills/page-visuals/scripts/` as the primary interface for Cowork or any runtime that only uploads the skill folder.
The repo-root `/scripts` copies are local development conveniences, not a packaging requirement.

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

When visuals are actually generated, extend the plan with provider metadata where possible:

```markdown
## Provider runs

| Shot | Provider | Brand context source | Source image IDs / refs | Result |
|---|---|---|---|---|
| hero-1 | bloom | repo profile + Bloom onboarding | bloom:img_123, local product ref | approved |
```

Also write `workspace/pages/[page-name]/visuals/manifest.json` with machine-readable fields for:
- provider used
- fallback provider and fallback reason when applicable
- Bloom brand ID and image IDs when applicable
- source refs used for the shot
- local output path
- status and notes

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
- attach or upload references before generation whenever the provider supports it

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

If Bloom is the first-pass provider and fails repeatedly:
- try provider-native edit/resize before full regeneration when the issue is composition or crop rather than core fidelity
- if Bloom still cannot clear QA, switch to Nano Banana
- if both providers fail and the shot is trust-critical, require real operator assets

Do not let Cowork quietly replace Bloom with its own default image behavior.
If the runtime cannot access Bloom, pause and say so.

## Eval Reference

For scoring criteria and pass thresholds, see `skills/page-qa/references/eval-rubric.md`.

## Hand-off

After visuals are approved, run `page-build`.
