---
name: landing-page-factory-orchestrator
description: "Top-level operator skill for Landing Page Factory. Classifies requests, chooses stage order, enforces prerequisites and hard stops, manages variant pages, reruns changed stages, and handles page-package admin."
metadata:
  openclaw:
    emoji: "🎛️"
    user-invocable: true
    requires:
      env: []
---

# Landing Page Factory Orchestrator

This is the control layer.

Use this skill when the request is about:
- building a full landing page pipeline
- creating one or more page variants
- rerunning selected stages after edits
- figuring out the right order of operations
- admin tasks around page package naming, artifact checks, cleanup, or memory logging

Do not replace the stage skills.
This skill routes and supervises them.

## What this skill owns

- request classification
- stage ordering
- artifact preflight checks
- hard-stop and downgrade enforcement
- page naming and variant naming
- deciding which stages must rerun after a change
- memory logging in `memory/YYYY-MM-DD.md`

## What this skill does not own

- extraction logic
- strategy logic
- copywriting logic
- image-generation logic
- HTML build logic
- QA scoring itself

Those belong to:
- `site-extract`
- `page-strategy`
- `brand-profile`
- `page-copy`
- `page-visuals`
- `page-build`
- `page-qa`

## Request classification

Route every request into one of these modes first.

### 1. Full pipeline
Examples:
- "Build me a landing page for https://example.com"
- "Run the whole thing for this brand"

Run in order:
1. `site-extract`
2. `page-strategy`
3. `brand-profile`
4. `page-copy`
5. `page-visuals`
6. `page-build`
7. `page-qa`

### 2. Variant pipeline
Examples:
- "Make a version for enterprise buyers"
- "Build three angle variants"

Use the existing brand artifacts if available.
Create a new page package per variant and rerun:
1. `page-strategy`
2. `page-copy`
3. `page-visuals`
4. `page-build`
5. `page-qa`

Rerun `site-extract` or `brand-profile` only if source facts changed or the current brand artifacts are missing or weak.

### 3. Stage rerun
Examples:
- "Rebuild visuals only"
- "Run QA again"
- "Update copy after strategy changes"

Only rerun the minimum necessary downstream stages.

Dependency rules:
- strategy changed → rerun copy, visuals, build, qa
- brand profile changed → rerun copy, visuals, build, qa
- copy changed → rerun build, qa
- visuals changed → rerun build, qa
- build changed → rerun qa

### 4. Admin / inspection
Examples:
- "What artifacts are missing?"
- "What order should we run this in?"
- "Create a new page package"

Inspect, report, and prepare. Do not fabricate missing artifacts.

## Preflight checks

Before invoking downstream work, verify required artifacts.

Brand-level:
- `workspace/brand/extract.md`
- `workspace/brand/extract.json`
- `workspace/brand/profile.md` when copy, visuals, or build need it
- `workspace/brand/palette.json` when visuals or build need it

Page-level:
- `workspace/pages/[page-name]/strategy.json`
- `workspace/pages/[page-name]/copy.md`
- `workspace/pages/[page-name]/visuals/`
- `workspace/pages/[page-name]/index.html`
- `workspace/pages/[page-name]/meta.json`
- `workspace/pages/[page-name]/qa.md`

If an artifact required for the requested stage is missing, stop and route to the earliest missing stage.

## Hard stops

Never continue past these:
- no `strategy.json` for copy, visuals, or build
- no unique mechanism identified
- no CTA destination for lead-gen or action-driven pages
- proof too thin for the proposed certainty level
- Firecrawl expected for extraction but not configured or runtime-blocked
- Bloom expected for visuals but not configured or runtime-blocked, unless the user explicitly approves Nano Banana or manual assets

When blocked, state:
1. what is missing
2. which stage must run next
3. what can be downgraded versus what cannot

## Downgrades

Continue with downgrade only when the stage skill allows it.

Typical downgrades:
- weak proof → softer claims, draft-only QA target
- partial visuals → neutral support layout
- exact-product image failure → branded environment or operator asset
- missing Bloom brand → onboard for provider context, but keep repo brand artifacts as source of truth

## Naming rules

Use descriptive page package names under `workspace/pages/`.

Pattern:
- base run: `[brand]-[core-angle]`
- variant run: `[brand]-[audience]-[angle]`

Good examples:
- `ridge-wallet-proof`
- `stealads-enterprise-time`
- `notion-agency-velocity`

Avoid:
- `test-page`
- `v2`
- `new-one`

## Variant workflow

When building multiple variants:
1. keep one shared brand source of truth in `workspace/brand/`
2. create a separate page package per variant
3. change audience, angle, offer framing, proof emphasis, or visual treatment deliberately
4. run full page-level downstream stages for each variant
5. compare QA verdicts and review flags across variants

Do not let variants silently overwrite each other.

## Stage ordering rules

Use this exact logic:

- If the user provides only a URL:
  start at `site-extract`

- If brand artifacts exist but page package does not:
  start at `page-strategy`

- If `strategy.json` exists and the user asks for copy:
  run `page-copy`

- If `copy.md` and brand artifacts exist and the user asks for visuals:
  run `page-visuals`

- If strategy, copy, and visuals exist:
  run `page-build`

- If build artifacts exist:
  run `page-qa`

## Build and visual script entrypoints

For Cowork and other skill-folder runtimes, prefer the skill-local scripts:

- `skills/landing-page-factory-orchestrator/scripts/page-admin.py`
- `skills/page-visuals/scripts/image-provider.sh`
- `skills/page-build/scripts/resolve-visual-assets.py`
- `skills/page-build/scripts/prepare-build-meta.py`
- `skills/page-build/scripts/select-build-images.py`
- `skills/page-build/scripts/html-image-context.py`
- `skills/page-build/scripts/build-page.py`

Repo-root `scripts/` entrypoints are local wrappers only.

Use the admin helper for orchestration support:

- `python3 skills/landing-page-factory-orchestrator/scripts/page-admin.py status --page-name [page-name]`
  Returns current artifact status and the earliest missing stage.

- `python3 skills/landing-page-factory-orchestrator/scripts/page-admin.py suggest-name --brand [brand] --audience [audience] --angle [angle]`
  Returns a clean, non-colliding page package name.

- `python3 skills/landing-page-factory-orchestrator/scripts/page-admin.py compare-variants --page-name [page-a] --page-name [page-b]`
  Returns a side-by-side JSON summary of artifact status, readiness score, readiness notes, headline, page type, CTA destination, image count, review flags, and QA verdict when present.

- `python3 skills/landing-page-factory-orchestrator/scripts/page-admin.py compare-variants --prefix [brand-prefix] --format markdown`
  Returns a human-readable markdown comparison table for Cowork reviews, ranked by readiness.

- `python3 skills/landing-page-factory-orchestrator/scripts/page-admin.py compare-variants --prefix [brand-prefix] --format markdown --output workspace/pages/[report-name].md`
  Writes the comparison report to disk.

- `python3 skills/landing-page-factory-orchestrator/scripts/page-admin.py compare-variants --prefix [brand-prefix]`
  Compares all page packages that match the prefix.

- `python3 skills/landing-page-factory-orchestrator/scripts/page-admin.py log-memory --title "[title]" --page-name [page-name] --stages "[stages]" --verdict "[verdict]"`
  Appends a short run log to `memory/YYYY-MM-DD.md`.

Use the runner when you want the orchestrator to actually execute the scripted parts of the pipeline:

- `python3 skills/landing-page-factory-orchestrator/scripts/run-pipeline.py --url https://example.com --page-name example-proof --format markdown`
  Runs extraction if needed, then stops at the next skill-authored stage with exact handoff instructions.

- `python3 skills/landing-page-factory-orchestrator/scripts/run-pipeline.py --page-name example-proof --format markdown`
  Resumes an existing page package and continues through the build chain when the required artifacts already exist.

- `python3 skills/landing-page-factory-orchestrator/scripts/run-pipeline.py --url https://example.com --brand Example --audience enterprise --angle time-saving --format markdown`
  Creates a non-colliding variant page name and runs until the next manual stage.

The runner is intentionally hybrid:
- it executes scripted stages directly
- it stops cleanly at `page-strategy`, `brand-profile`, `page-copy`, and most `page-visuals` work when authored artifacts are still missing
- it resumes automatically once those artifacts exist

Extraction policy:
- prefer Firecrawl automatically when `FIRECRAWL_API_KEY` is available
- if Firecrawl is not configured, basic extraction is allowed but should be treated as a downgrade
- for public-release-quality runs, recommend adding Firecrawl rather than silently acting like the extraction quality is equivalent

Provider enforcement:
- do not allow `site-extract` to quietly collapse into WebFetch/manual scraping when Firecrawl is the intended path
- do not allow `page-visuals` to quietly collapse into default built-in image generation when Bloom is the intended path
- if the preferred provider is blocked, missing, or not configured, pause and ask the operator which downgrade is acceptable
- only continue with a downgrade when the user explicitly approves it

Cowork-specific behavior:
- if Cowork blocks `api.firecrawl.dev`, say so directly and recommend either allowlisting the domain or running the local extraction preflight
- if Cowork cannot reach Bloom, say so directly and ask whether to configure Bloom, use Nano Banana, or proceed with manual assets
- do not let “it kind of worked with WebFetch/default images” count as a successful provider run

Do not claim full automation for stages that still depend on skill-authored judgment.

## Memory logging

After any meaningful run, append a short note to `memory/YYYY-MM-DD.md` with:
- brand or page name
- stages completed
- QA verdict if available
- blockers or downgrades
- notable lessons

Keep it terse. One short section per run is enough.

## Output expectations

When orchestrating, always report:
- chosen mode: full pipeline, variant, stage rerun, or admin
- page package name(s)
- stages run or next stages required
- blockers, downgrades, or review flags

For variant runs, include a flat comparison:
- variant name
- audience / angle
- current artifact status
- QA verdict if present
