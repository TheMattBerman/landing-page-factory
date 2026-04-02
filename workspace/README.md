# Workspace

This directory stores all generated artifacts from Page Factory runs.

## brand/

Shared brand data used across all pages:

| File | Purpose |
|------|---------|
| `extract.md` | Raw site extraction — claims, proof, CTAs, trust cues, visual identity |
| `extract.json` | Machine-readable extraction |
| `profile.md` | Evidence-backed brand voice + visual system |
| `palette.json` | Color system, typography, spacing |

## pages/

Each page gets its own directory with a complete artifact package:

```
pages/[page-name]/
├── strategy.md        # Mechanism map, claims control, routing decision
├── strategy.json      # Machine-readable strategy
├── copy.md            # Full conversion copy with sharpness audit
├── visuals/
│   ├── index.md       # Shot plan with preservation classes
│   ├── manifest.json  # Machine-readable provider runs, refs, remote IDs, fallback history
│   └── *.jpg          # Generated images
├── index.html         # Deployable single-file HTML page
├── meta.json          # Build metadata, proof provenance, confidence
└── qa.md              # QA report with shippability verdict
```

Brand data is shared across pages. Strategy, copy, visuals, and build are per-page.

Build helper:
- `scripts/resolve-visual-assets.py --page-name [page-name]`
  This resolves `visuals/manifest.json` into build-ready image metadata for HTML assembly and `meta.json`.
- `scripts/prepare-build-meta.py --page-name [page-name] --resolved-assets [file]`
  This merges resolved visual assets into `meta.json`, including deterministic hero/mechanism/lifestyle image picks.
- `scripts/select-build-images.py --meta workspace/pages/[page-name]/meta.json`
  This emits the final builder slot object for hero, mechanism, lifestyle, and OG image selection.
- `scripts/html-image-context.py --meta workspace/pages/[page-name]/meta.json`
  This emits literal HTML-ready image values and default alt text for the chosen slots.
- `scripts/build-page.py --page-name [page-name]`
  This writes a minimal real `index.html` scaffold using strategy, meta, and HTML-ready image values.
