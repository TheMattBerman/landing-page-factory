# Landing Page Factory — Setup Guide

Pick your path. Same skills, same pipeline, same output — different interfaces.

---

## Path A: Claude Cowork (No Terminal Required)

**Time to first page: ~2 minutes**

Best for: Marketers, founders, anyone who wants to build landing pages without touching a terminal.

### Step 1: Download the Kit

Download this repo as a ZIP from GitHub, or clone it if you're comfortable with git.

### Step 2: Create a Claude Project

1. Go to [claude.ai](https://claude.ai)
2. Create a new Project (or open an existing one)
3. In Project Knowledge, upload these folders:
   - `skills/` — all 7 skill folders
   - `references/` — eval rubric and anti-slop reference

That's the entire setup.

### Step 3: Build Your First Page

Start a new conversation in your project and say:

```
Build me a landing page for https://ridgewallet.com
```

Claude reads the skills automatically, runs the 7-stage pipeline, and produces:
- Brand extraction with proof inventory
- Page strategy with mechanism map
- Conversion copy with sharpness audit
- Visual shot plan
- Single-file HTML page
- QA report with shippability verdict

### Tips for Claude Cowork

**Build variants:**
```
Now build a version targeting women 25-35 with the time-saving angle
```

**Upload your own images:**
Drop product photos into the conversation. Claude uses them instead of generating images, which gives better product fidelity.

**Score the output:**
```
Run the sharpness audit on this copy
```
```
Score this page against the eval rubric
```

**Multi-page sessions:**
Extract the brand once, then build multiple pages in the same conversation:
```
Build me a landing page for https://mysite.com
```
Then:
```
Now build one for the enterprise audience
Now build one with the cost-saving angle
Now build one for the UK market
```

The brand data persists in the conversation — each variant only needs new strategy, copy, and build.

---

## Path B: OpenClaw (Agent Framework)

**Time to first page: ~10 minutes**

Best for: Developers, agencies, power users who want automation, cron jobs, and multi-agent orchestration.

### Step 1: Install

```bash
# Install OpenClaw (if you haven't already)
npm install -g openclaw

# Clone the kit
git clone https://github.com/themattberman/landing-page-factory.git
cd landing-page-factory

# Run install
bash install.sh

# Verify
bash doctor.sh
```

### Step 2: Configure (Optional)

```bash
cp .env.example .env
# Add your Firecrawl API key for deep extraction
# Add your Bloom API key if you want Bloom as first-pass image generation
# Without Firecrawl, extraction still works but with reduced coverage
```

Recommended image provider order for OpenClaw:
- Bloom first pass for on-brand generation
- Nano Banana fallback if Bloom is unavailable, credits are exhausted, or exact-product QA fails
- Manual assets for trust-critical product photography when model fidelity is not good enough

### Step 3: Start the Agent

```bash
openclaw start
```

Then message naturally:

```
Build me a landing page for https://ridgewallet.com
```

Or run stages individually:

```bash
/site-extract https://ridgewallet.com --deep
/page-strategy --page ridge-wallet-v1
/brand-profile
/page-copy --page ridge-wallet-v1
/page-visuals --page ridge-wallet-v1
/page-build --page ridge-wallet-v1
/page-qa --page ridge-wallet-v1
```

### Step 4: Review Output

```
workspace/pages/ridge-wallet-v1/
├── strategy.md + strategy.json
├── copy.md
├── visuals/
│   ├── manifest.json
├── index.html          ← open in browser
├── meta.json
└── qa.md               ← check the verdict
```

### Compare Variants

```bash
bash scripts/eval-summary.sh
```

Output:
```
ridge-wallet-v1: SHIPPABLE | copy: 8.3 | visual: 8.5 | qa: 8.4 | overall: 8.4
ridge-wallet-time: SHIPPABLE | copy: 8.7 | visual: 8.1 | qa: 8.3 | overall: 8.3
ridge-wallet-enterprise: DRAFT ONLY | copy: 7.9 | visual: 7.5 | qa: 7.6 | overall: 7.7
```

### Chain With Other Kits

```
Meta Ads Kit → find winning angles
Landing Page Factory → build matched pages for each angle
Deploy to Vercel/Netlify
Meta Ads Kit → monitor performance
Iterate
```

---

## Path C: Hermes / Other Agent Frameworks

**Time to first page: ~5 minutes**

Best for: Users of Hermes, Cursor, Windsurf, or custom agent setups.

### Hermes
Copy `skills/` and `references/` into your Hermes workspace. The agent discovers them automatically.

### Cursor / Windsurf / Cline
Add the skill SKILL.md files as project rules or context. The pipeline logic is in the markdown — any LLM that can follow instructions can run it.

### Custom / DIY
Feed the SKILL.md contents as system context. The skills are self-contained — they describe inputs, outputs, rules, and hand-off logic. No proprietary runtime needed.

---

## Firecrawl Setup (All Paths)

[Firecrawl](https://firecrawl.dev) provides deep site extraction and should be treated as the recommended default for public-release work.
It scrapes multiple pages for better proof, pricing, objection, and trust cue coverage.

1. Sign up at [firecrawl.dev](https://firecrawl.dev) (free tier available)
2. Get your API key
3. Set it however your platform expects:
   - **OpenClaw:** `export FIRECRAWL_API_KEY=your_key` or add to `.env`
   - **Claude Cowork:** provide the key in whatever project/runtime path your setup supports, or explicitly tell Claude to use Firecrawl when available
   - **Other:** Pass the key to the extraction scripts

The orchestrator and extraction scripts auto-detect `FIRECRAWL_API_KEY`.

**Without Firecrawl:** the system still works, but it is running in reduced mode. Basic extraction covers single pages reasonably well, but it is weaker for:
- proof-heavy sites
- testimonials spread across multiple pages
- pricing pages
- case studies
- trust cues that live outside the homepage

For public-release-quality runs, use Firecrawl.

---

## Bloom Setup (Recommended For Images)

[Bloom](https://go.trybloom.ai/matthew-berman) is the recommended first-pass provider for `page-visuals`.

Important boundary:
- Page Factory brand discovery remains the source of truth.
- Bloom brand onboarding exists to give the image provider usable brand context, not to replace `site-extract` or `brand-profile`.

Recommended workflow:
1. Run `site-extract` and `brand-profile` as usual.
2. When generating visuals, check whether the brand already exists in Bloom.
3. If not, onboard the brand in Bloom from the site URL.
4. If Bloom needs more help, fill in its brand context from `workspace/brand/extract.md`, `workspace/brand/profile.md`, and `workspace/brand/palette.json`.
5. Generate with Bloom first.
6. Fall back to Nano Banana if Bloom is unavailable, out of credits, or cannot clear the visual QA bar.

What Bloom supports from its current developer docs:
- Brand onboarding from a website or Instagram URL
- Async image generation with variants
- Image editing and resizing
- Reference-image uploads for exact-product or packaging preservation
- Credit checks

Get started:
- Referral link: [go.trybloom.ai/matthew-berman](https://go.trybloom.ai/matthew-berman)
- Developer docs: [trybloom.ai/developers](https://www.trybloom.ai/developers/)

Suggested environment variables:

```bash
# Preferred image provider for first-pass generation
IMAGE_PROVIDER=bloom

# Bloom API key
BLOOM_API_KEY=your_key_here

# Optional documented fallback
IMAGE_FALLBACK_PROVIDER=nano-banana

# Optional external command hook for Nano Banana
NANO_BANANA_COMMAND="/path/to/your/nano-banana-adapter"
```

---

## Building Variant Pages

The real power is building multiple pages from the same brand.

### Same brand, different angles
```
Build a page with the time-saving angle
Build a page with the status angle
Build a page with the cost-reduction angle
```

### Same brand, different audiences
```
Build a page targeting enterprise CTOs
Build a page targeting startup founders
Build a page targeting marketing directors
```

### Same brand, different geos
```
Build a page for the US market
Build a page for the UK market (British English, GBP pricing)
Build a page for the DACH region (German)
```

The brand extract and profile are shared. Strategy, copy, visuals, and build are per-page.

---

## Combining With Other Kits

### Meta Ads Kit → Landing Page Factory
1. Meta Ads Kit finds winning ad angles and detects fatigue
2. Landing Page Factory builds a matched page for each winning angle
3. Deploy pages
4. Meta Ads Kit monitors click-to-conversion performance
5. Iterate: kill underperformers, build new variants for emerging winners

### SEO Kit → Landing Page Factory
1. SEO Kit discovers keyword opportunities (positions 5-20)
2. Landing Page Factory builds SEO-optimized pages per keyword cluster
3. Deploy
4. SEO Kit monitors ranking movement
5. Iterate based on what's climbing

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Mechanism unclear" — pipeline stops at strategy | Source site doesn't explain *why* the product works. Provide a manual brief or extract from additional product pages. |
| "Proof too thin" — page marked Draft Only | Not enough verifiable proof found on source. Add proof manually or accept softer claims. |
| Image gen can't match exact product | AI struggles with exact product fidelity. Provide real product photos or let it downgrade to branded environment. |
| Firecrawl rate limited | Free tier has limits. Wait and retry, or use basic extraction. |
| Claude runs out of context in a long session | Start a new conversation for each brand. Variants of the same brand can share a conversation. |

---

Questions? [Open an issue](https://github.com/themattberman/landing-page-factory/issues) or find me on [Twitter/X](https://twitter.com/themattberman).
