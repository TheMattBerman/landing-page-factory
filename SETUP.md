# Landing Page Factory — Setup Guide

Get your AI landing page builder running in 5 minutes.

---

## Step 1: Clone and Install

```bash
git clone https://github.com/themattberman/landing-page-factory.git
cd landing-page-factory
bash install.sh
```

This creates the workspace directories and checks dependencies.

---

## Step 2: Verify Setup

```bash
bash doctor.sh
```

You should see all green checks. The health check verifies:
- All 7 skills are present
- Required dependencies (curl, python3) are installed
- Optional dependencies (jq) noted
- Workspace directories exist

---

## Step 3: Configure Firecrawl (Optional, Recommended)

[Firecrawl](https://firecrawl.dev) provides deep site extraction — multiple pages, structured data, better coverage.

1. Sign up at [firecrawl.dev](https://firecrawl.dev) (free tier available)
2. Get your API key
3. Set it:

```bash
cp .env.example .env
# Edit .env and add your key
```

Or export directly:

```bash
export FIRECRAWL_API_KEY=your_key_here
```

**Without Firecrawl:** The kit falls back to basic extraction (curl + readability). Works fine for simple sites, but deep extraction covers more pages and gets better proof/trust cue coverage.

---

## Step 4: Image Generation

Page Visuals uses whatever image generation model your OpenClaw instance has configured.

Supported providers:
- **OpenAI** — DALL-E 3, GPT Image
- **Google** — Gemini image generation
- **Fal.ai** — Various models
- **Any provider** configured in OpenClaw

No additional setup needed — it uses your existing OpenClaw image generation config.

If no image generation is configured, the visual stage will create shot plans but skip generation. You can provide your own images instead.

---

## Step 5: Run Your First Page

### With OpenClaw (recommended)

```bash
openclaw start
```

Then message:

```
Build me a landing page for https://ridgewallet.com
```

The agent runs the full 7-stage pipeline and produces a complete page package.

### Manual (stage by stage)

```bash
# 1. Extract brand facts from URL
/site-extract https://ridgewallet.com --deep

# 2. Create page strategy
/page-strategy --page my-first-page

# 3. Build brand profile
/brand-profile

# 4. Write copy
/page-copy --page my-first-page

# 5. Generate visuals
/page-visuals --page my-first-page

# 6. Build the page
/page-build --page my-first-page

# 7. Run QA
/page-qa --page my-first-page
```

---

## Step 6: Review Your Output

After a successful run, check `workspace/pages/[page-name]/`:

```
workspace/pages/my-first-page/
├── strategy.md        # Mechanism map, claims control
├── strategy.json      # Machine-readable strategy
├── copy.md            # Full copy with sharpness audit
├── visuals/
│   ├── index.md       # Shot plan
│   └── *.jpg          # Generated images
├── index.html         # The page (open in browser)
├── meta.json          # Build metadata
└── qa.md              # QA report + verdict
```

Open `index.html` in your browser to preview. Check `qa.md` for the shippability verdict.

---

## Building Variant Pages

The real power is building multiple pages from the same brand:

```bash
# Same brand, different angle
/page-strategy --page ridge-time-saving    # Time-saving angle
/page-strategy --page ridge-status         # Status angle
/page-strategy --page ridge-enterprise     # Enterprise audience

# Each gets its own copy, visuals, build, QA
/page-copy --page ridge-time-saving
/page-build --page ridge-time-saving
# ... etc
```

The brand extract and profile are shared. Strategy, copy, visuals, and build are per-page.

---

## Combining With Other Kits

### Meta Ads Kit → Landing Page Factory

```
1. Meta Ads Kit finds winning ad angles
2. Landing Page Factory builds a page matching each angle
3. Deploy pages
4. Meta Ads Kit monitors performance
5. Iterate
```

### SEO Kit → Landing Page Factory

```
1. SEO Kit discovers keyword opportunities
2. Landing Page Factory builds SEO-optimized pages per keyword cluster
3. Deploy
4. SEO Kit monitors rankings
```

---

## Troubleshooting

**"Mechanism unclear" — pipeline stopped at strategy**
The source site doesn't clearly explain *why* the product works. Provide a manual brief with mechanism details, or extract from additional product pages.

**"Proof too thin" — page marked Draft Only**
Not enough verifiable proof (testimonials, stats, logos) found on the source site. Add proof manually or use softer claims.

**"Image gen failing on exact product"**
AI image generation struggles with exact product fidelity. Provide real product photos, or let the system downgrade to branded environment visuals.

**"Firecrawl rate limited"**
The free tier has limits. Wait and retry, or use basic extraction as fallback.

---

## What's Next

Once you're comfortable with single pages, try:

1. **Batch generation** — Multiple pages from one brand, different angles
2. **A/B variants** — Same page, different headlines or CTAs
3. **Campaign pairing** — Match pages to specific ad creatives
4. **Multi-brand** — Run the pipeline for different clients

---

Questions? [Open an issue](https://github.com/themattberman/landing-page-factory/issues) or find me on [Twitter/X](https://twitter.com/themattberman).
