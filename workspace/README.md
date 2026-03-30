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
│   └── *.jpg          # Generated images
├── index.html         # Deployable single-file HTML page
├── meta.json          # Build metadata, proof provenance, confidence
└── qa.md              # QA report with shippability verdict
```

Brand data is shared across pages. Strategy, copy, visuals, and build are per-page.
