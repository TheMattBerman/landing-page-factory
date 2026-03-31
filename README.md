# Landing Page Factory

An AI agent that turns any URL into a deployable landing page — with real brand voice, real proof, and zero AI slop.

Works with [Claude Cowork](https://claude.ai), [OpenClaw](https://openclaw.ai), or any agent framework that supports skills.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

**Extract → Strategize → Profile → Write → Visual → Build → QA → Ship**

This kit automates the entire landing page pipeline:

- **Site Extract** — Scrape any URL for claims, proof, CTAs, mechanism language, trust cues, and visual identity
- **Page Strategy** — Map the mechanism, control claims, plan proof placement, route by page type
- **Brand Profile** — Build an evidence-backed voice and visual system (not AI guesswork)
- **Page Copy** — Write conversion copy with claim control, sharpness audit, and mandatory reduction pass
- **Page Visuals** — Generate images by preservation class — exact product, branded environment, or concept support
- **Page Build** — Assemble a responsive single-file HTML page with category-aware layout routing
- **Page QA** — Final gate against mechanism preservation, proof discipline, trust cues, and anti-slop compliance

The result: A complete landing page package from a URL — strategy doc, copy, visuals, HTML, metadata, and QA report.

---

## Why This Exists

I've spent 20 years in marketing. Scaled Fireball Whisky from one state to a billion-dollar global brand. Ran campaigns for Heineken, Hennessy, Buffalo Trace. Now I run [Emerald Digital](https://emerald.digital), an AI-first marketing agency.

Here's what I learned: The bottleneck in paid media isn't the ads. It's the landing pages.

You can spin up 50 ad variants in Meta in an hour. Different angles, different segments, different hooks. But they all point to the same landing page. The ad says "save 3 hours a week" and the landing page says "the most powerful platform for teams." Disconnect. The click dies.

Every marketer knows the ad-to-page experience should be seamless. Nobody does it because building a unique landing page per ad angle is physically impossible at human speed.

**The matrix:**

```
Products × Segments × Angles × Geos = Hundreds of pages nobody has time to build
```

This kit makes that possible. Not with generic AI slop — with a controlled pipeline that preserves your brand's actual mechanism, proof, and trust cues.

If you're running my [Meta Ads Kit](https://github.com/themattberman/meta-ads-kit) or [Google Ads Kit](https://github.com/themattberman/google-ads-copilot), this is the missing piece. Pair it with [StealAds](https://stealads.ai) for psychology-driven ad creative generation, and you have the full loop: winning ad angles, matched landing pages, and creative that converts.

---

## Quick Start

### Option A: Claude Cowork (Easiest — no setup required)

If you use [Claude](https://claude.ai) with Cowork, this is the simplest path:

1. Download this repo (or clone it)
2. Add the `skills/` folder to your Claude Cowork project
3. Start a conversation and say:

```
Build me a landing page for https://ridgewallet.com
```

Claude reads the skills, runs the pipeline, and produces the full page package. No terminal, no installation, no config files.

**That's it.** Claude handles extraction, strategy, copy, visuals, build, and QA — all guided by the skills in this repo.

> **Tip:** For best results, also add `references/eval-rubric.md` and `references/anti-slop.md` to your project so Claude can score and QA the output.

### Option B: OpenClaw (Full agent framework)

For developers and power users who want automation, cron jobs, and multi-agent orchestration:

```bash
git clone https://github.com/themattberman/landing-page-factory.git
cd landing-page-factory

# Install dependencies and workspace
bash install.sh

# Verify everything is set up
bash doctor.sh

# Start the agent
openclaw start
```

Then message it naturally:

```
Build me a landing page for https://ridgewallet.com
```

Or run each stage individually:

```bash
/site-extract https://ridgewallet.com --deep
/page-strategy --page ridge-wallet-v1
/brand-profile
/page-copy --page ridge-wallet-v1
/page-visuals --page ridge-wallet-v1
/page-build --page ridge-wallet-v1
/page-qa --page ridge-wallet-v1
```

### Option C: Any Agent Framework

The skills are plain markdown files. They work with any AI agent that can read instructions:

- **Hermes** — Drop skills into your workspace
- **Cursor / Windsurf** — Add as project context
- **Custom setups** — Feed the SKILL.md files as system context

The pipeline logic lives in the skills themselves, not in proprietary tooling.

---

## The Pipeline

Most AI landing page tools skip straight to generation. That's why they produce slop.

This kit forces a **7-stage pipeline** where each stage produces an explicit artifact that the next stage reads. No vibes. No hallucinated proof. No generic premium-tech sludge.

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Site Extract │───▶│   Strategy   │───▶│    Brand     │───▶│    Copy      │
│  (scrape URL) │    │  (mechanism  │    │  (voice +    │    │  (claim      │
│               │    │   + routing) │    │   visual ID) │    │   control)   │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
                                                                   │
                    ┌──────────────┐    ┌──────────────┐           │
                    │     QA       │◀───│    Build     │◀──────────┤
                    │  (final gate)│    │  (HTML page) │    ┌──────┴──────┐
                    └──────────────┘    └──────────────┘    │   Visuals   │
                                                            │ (by class)  │
                                                            └─────────────┘
```

### What makes this different from "ask ChatGPT to make a landing page"

1. **Mechanism preservation** — The page explains *why* the product works, not just that it exists
2. **Proof discipline** — Every stat, testimonial, and trust badge is provenance-tagged. Nothing invented.
3. **Claim control** — Allowed claims vs. forbidden claims are explicit. No unearned certainty.
4. **Page-type routing** — Physical product pages route differently from SaaS, lead gen, or regulated niches
5. **Anti-slop design** — Banned patterns list prevents the page from looking like every other AI-generated site
6. **Mandatory QA** — Final gate checks mechanism, proof, trust, accessibility, and shippability

---

## Skills

| Skill | What It Does |
|-------|-------------|
| `site-extract` | Scrape a URL for exact claims, proof, CTAs, mechanism language, trust cues, visual identity, and page patterns |
| `page-strategy` | Map the mechanism, normalize the offer, control claims, route by page type, flag review items |
| `brand-profile` | Build evidence-backed voice + visual system. Layer 1: observed facts. Layer 2: synthesis. |
| `page-copy` | Write conversion copy with hard ban list, sharpness audit, and mandatory 20% reduction pass |
| `page-visuals` | Plan and generate visuals by preservation class — exact product, branded environment, or concept support |
| `page-build` | Assemble responsive single-file HTML with preservation hierarchy and category-aware layout routing |
| `page-qa` | Final quality gate — mechanism, proof, trust, copy, visuals, build quality, anti-slop compliance |

### The Full Loop

```
Extract (facts) → Strategy (decisions) → Profile (brand) → Copy (words) → Visuals (images) → Build (page) → QA (gate)
```

Every stage reads from the previous stage's artifacts. No stage hallucinates inputs.

---

## How It Works

### Stage 1: Site Extract
Give it a URL. It scrapes and returns:
- Exact hero language (quoted, not paraphrased)
- Claim inventory with provenance tags
- Proof inventory (testimonials, stats, logos, guarantees)
- CTA inventory
- Mechanism language
- Trust cues
- Visual identity
- Page patterns

Uses [Firecrawl](https://firecrawl.dev) for deep extraction, falls back to basic scraping.

### Stage 2: Page Strategy
The decision layer most tools skip entirely. Determines:
- What the unique mechanism is
- What claims are allowed vs. forbidden
- What proof is shippable vs. placeholder
- What page type to build (product-led, SaaS, lead gen, regulated)
- What must be preserved from the source

**No strategy artifact = no page.** This is enforced.

### Stage 3: Brand Profile
Separates observed evidence from synthesis:
- **Layer 1:** Exact phrases, claim inventory, visual motifs — things we *saw*
- **Layer 2:** Positioning, voice system, language bank — things we *inferred*

Downstream skills know which layer they're reading from.

### Stage 4: Page Copy
Writes from strategy + language bank, not from vibes. Includes:
- Hard ban list (elevate, seamless, unlock, next-gen, cutting-edge, revolutionize...)
- Mandatory sharpness audit (mechanism clarity, specificity, proof density, phrase originality)
- Mandatory reduction pass (cut 20% of lines that are redundant or self-congratulatory)

### Stage 5: Page Visuals
Every image is classified before generation:
- **Exact product** — preserve silhouette, proportions, materials, packaging
- **Branded environment** — match palette and audience world, avoid stock-photo staging
- **Concept support** — atmospheric, subordinate to copy, no fake product details

### Stage 6: Page Build
Assembles the HTML with a **preservation hierarchy**:
1. Trust-critical category conventions
2. Mechanism communication needs
3. Brand visual identity
4. Layout rhythm improvements
5. Anti-slop taste (only where it doesn't distort 1-4)

Routes by page type: product-led, SaaS/app, lead capture, authority/service, regulated.

### Stage 7: Page QA
Final gate scores 7 dimensions:
- Mechanism preservation
- Proof discipline
- Trust cue preservation
- Copy sharpness
- Visual fidelity
- Build quality
- Anti-slop compliance

Verdict: **Shippable**, **Draft only**, or **Blocked**. No page ships without passing QA.

---

## Non-Negotiables

These are hard rules baked into every stage:

1. **Preserve mechanism before improving aesthetics.** A pretty page that weakens the mechanism is a bad page.
2. **Preserve proof integrity.** Never invent testimonials, stats, logos, awards, or guarantees.
3. **Stop or downgrade when source signal is weak.** Don't fake confidence.
4. **Preserve trust-critical category conventions.** Don't redesign trust away.
5. **Every downstream stage reads from explicit artifacts, not vibes.**

---

## Output

Every completed run produces a full page package:

```
workspace/pages/[page-name]/
├── strategy.md        # Mechanism map, claims control, routing decision
├── strategy.json      # Machine-readable strategy
├── copy.md            # Full copy with sharpness audit
├── visuals/
│   ├── index.md       # Shot plan with preservation classes
│   ├── hero-1.jpg     # Generated images
│   ├── product-1.jpg
│   └── lifestyle-1.jpg
├── index.html         # Deployable single-file HTML page
├── meta.json          # Build metadata, proof provenance, confidence
└── qa.md              # QA report with shippability verdict
```

---

## The Scale Play

This isn't about making one landing page faster. It's about making *message match at scale* possible.

**Before:** 50 ad variants → 1 landing page → disconnect → wasted spend

**After:** 50 ad variants → 50 matched landing pages → each one speaks the same language as the ad that sent the visitor there

Different products. Different audience segments. Different psychological angles (time, money, control, status). Different geographies. Each one gets a page that matches.

If you're running [Meta Ads Kit](https://github.com/themattberman/meta-ads-kit) or [Google Ads Kit](https://github.com/themattberman/google-ads-copilot), this closes the loop from ad to conversion. Add [StealAds](https://stealads.ai) for AI-generated ad creative that decodes the psychology behind winning ads, and every step from creative to click to conversion is matched.

---

## Platform Guide

### Claude Cowork

The simplest way to use Landing Page Factory. No installation, no terminal.

**Setup:**
1. Open [Claude](https://claude.ai) and create a new project
2. Upload the `skills/` folder and `references/` folder to your project
3. Start chatting

**What you can say:**
- "Build me a landing page for https://ridgewallet.com"
- "Extract the brand from https://linear.app"
- "Create a lead gen page for my consulting service"
- "Build a page targeting enterprise buyers, time-saving angle"
- "Run QA on the ridge-wallet page"

Claude reads the skills, follows the pipeline, and produces all the artifacts — strategy docs, copy, visuals, HTML, and QA report.

**Tips for Cowork:**
- Upload your own product images for better visual fidelity
- Ask Claude to build multiple variants: "Now build one for the time-saving angle" and "Now one for enterprise buyers"
- Say "Run the sharpness audit" to get scored quality metrics on any copy

### OpenClaw

For developers who want persistent agents, cron automation, and multi-agent workflows:

```bash
npm install -g openclaw
cd landing-page-factory
openclaw start
```

Message it naturally — same commands as Cowork. Plus:
- Schedule batch page generation
- Chain with [Meta Ads Kit](https://github.com/themattberman/meta-ads-kit), [SEO Kit](https://github.com/themattberman/seo-kit), or [StealAds](https://stealads.ai)
- Run QA across variants with `bash scripts/eval-summary.sh`

### Hermes / Other Frameworks

The skills are portable markdown files. Drop them into any agent workspace:

- **Hermes** — Copy `skills/` to your workspace. The agent picks them up automatically.
- **Cursor / Windsurf / Cline** — Add skills as project rules or context files
- **Custom agents** — Feed the SKILL.md contents as system context or tool definitions

The pipeline logic lives in the skills, not in proprietary tooling. Any LLM that can follow structured instructions can run this.

### Automate It

Combine with other kits for a full campaign pipeline:

```
StealAds (decode ad psychology) → Meta Ads Kit (find winning angles) → Landing Page Factory (build matched pages) → Deploy → Monitor
```

---

## Configuration

### Firecrawl (optional, recommended)

For deep site extraction (multiple pages, structured data, better proof coverage):

```bash
export FIRECRAWL_API_KEY=your_key_here
```

Get a key at [firecrawl.dev](https://firecrawl.dev). Free tier works fine for most sites.

Without Firecrawl, the kit falls back to basic scraping. Works fine for simple sites.

> **Claude Cowork users:** You can skip Firecrawl entirely. Just paste the URL and Claude will extract what it can from the page directly.

### Image Generation

Page Visuals works with whatever image generation is available in your setup:
- **Claude Cowork** — Uses Claude's built-in image generation
- **OpenClaw** — Uses your configured provider (OpenAI, Google, Fal.ai, etc.)
- **Manual** — Skip generation and provide your own product photos

---

## Cost

| Setup | Monthly Cost |
|-------|-------------|
| Claude Cowork | Included with Claude Pro/Team subscription |
| OpenClaw | Free (open source) |
| Firecrawl | Free tier available |
| Image gen | Depends on provider |
| **Skills themselves** | **Free forever** (MIT licensed) |

---

## Project Structure

```
landing-page-factory/
├── README.md              # You're here
├── SETUP.md               # Detailed setup guide
├── SOUL.md                # Agent personality (for OpenClaw/Hermes)
├── AGENTS.md              # Agent instructions (for OpenClaw/Hermes)
├── skills/                # ← THE CORE (works with any agent)
│   ├── site-extract/         # URL → raw facts, proof, trust cues
│   │   └── scripts/          # Firecrawl + fallback extraction
│   ├── page-strategy/        # Facts → mechanism map, claims control
│   ├── brand-profile/        # Extract → evidence-backed voice + visuals
│   ├── page-copy/            # Strategy → conversion copy with QA
│   ├── page-visuals/         # Strategy → preservation-classed images
│   ├── page-build/           # Everything → deployable HTML page
│   │   └── references/       # Anti-slop design patterns
│   └── page-qa/              # Final shippability gate
│       ├── references/       # Eval rubric + scoring system
│       └── scripts/          # eval-summary.sh (variant comparison)
├── examples/
│   └── ridge-wallet-preview/ # Complete demo page package
├── workspace/
│   ├── brand/                # Brand extract, profile, palette
│   └── pages/                # Generated page packages
├── install.sh             # Quick install (OpenClaw)
├── doctor.sh              # Health check (OpenClaw)
└── .env.example           # Environment template
```

> **Claude Cowork users:** You only need the `skills/` and `references/` folders. Everything else is for agent framework setups.

---

## Anti-Slop Design

Every AI landing page generator produces the same thing: purple gradients, Inter font, three equal feature cards, vague "unlock your potential" copy, fake trust badges.

This kit includes a **banned patterns list** and a **preservation hierarchy** that prevents that:

**Banned:**
- Inter as default font (unless the brand actually uses it)
- Purple/blue AI gradients
- Card soup (three equal cards by default)
- Generic system fonts over real brand typography
- Vague premium-tech language
- Fake precision numbers
- Stock trust-badge lookalikes

**Required:**
- One dominant idea per section
- Real CTA above fold
- Visible trust cue above fold
- Proof placed where it reduces friction
- Intentional font pairing or faithful brand font usage
- Varied section pacing (not uniform spacing)

Anti-slop applies *after* brand fidelity, not before. If an anti-slop rule conflicts with a legitimate trust convention, the trust convention wins.

---

## Proof Classes

Every proof element in the system carries provenance:

| Class | Meaning | Shippable? |
|-------|---------|-----------|
| `verified_source` | Directly observed on source site | ✅ Yes |
| `derived_source` | Inferred from source with clear reasoning | ✅ Yes |
| `placeholder_draft` | Placeholder for review | ❌ No |
| `missing` | Not found in source | ❌ No |

Non-shippable proof is flagged in QA. Pages with critical proof gaps get a "Draft only" or "Blocked" verdict.

---

## Contributing

This is open source. PRs welcome.

Ideas for contribution:
- Template library for common page types
- Deployment integrations (Vercel, Netlify, Cloudflare Pages)
- A/B test variant generation
- Multi-language support
- CMS integration (WordPress, Webflow, Framer)
- Analytics and heatmap integration

---

MIT License. Use it, fork it, build on it.

---

Built by [Matt Berman](https://twitter.com/themattberman).

- 🐦 Twitter/X: [@themattberman](https://twitter.com/themattberman)
- 📰 Newsletter: [Big Players](https://bigplayers.co)
- 🏢 Agency: [Emerald Digital](https://emerald.digital)

---

Stop building one landing page and hoping it works for everyone. Build the page that matches every ad, every segment, every angle.

Star the repo if this helps. It tells me to keep building.
