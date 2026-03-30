---
name: site-extract
description: "Extract operator-grade source facts from a website or manual brief: claims, proof, CTAs, mechanism language, trust cues, visual patterns, and page structure with provenance. First stage of Page Factory."
metadata:
  openclaw:
    emoji: "🔍"
    user-invocable: true
    requires:
      env:
        - FIRECRAWL_API_KEY
---

# Site Extract

Use this when a user gives a site URL and wants a landing page built without a bloated intake process.

This stage does not synthesize. It extracts.

If you cannot trace a claim, proof point, or trust cue back to the source, label it missing or inferred. Do not quietly upgrade it into fact.

## Required inputs

- primary URL
- optional product URL
- optional `--deep`
- optional manual brief snippets if source access is incomplete

## Operator goal

Build a source record that downstream skills can trust.

That means extracting:
- exact claim language
- exact CTA language
- exact proof points
- visible page patterns
- mechanism language
- trust cues
- visual identity
- category conventions

## Output files

Write:
- `workspace/brand/extract.md`
- `workspace/brand/extract.json`
- `workspace/brand/palette.json`

## Hard extraction rules

1. Preserve exact language where possible. Quote, do not paraphrase.
2. Tag provenance for every proof item and major claim.
3. Distinguish observed facts from inference.
4. If source signal is thin, say it directly.
5. If mechanism is unclear after extraction, downstream strategy must stop until resolved.

## Required extract structure

```markdown
# Brand Extract: [Brand]
Source URLs:
- [url 1]
- [url 2]
Extracted: [date]
Confidence: high | medium | low

## 1. Brand + category
- Brand name:
- Product category:
- Primary offer:
- Business model:
- Geography / market hints:

## 2. Exact hero language
| Element | Exact text | Source URL | Provenance |
|---|---|---|---|
| Headline | | | observed |
| Subheadline | | | observed |
| Primary CTA | | | observed |
| Secondary CTA | | | observed |

## 3. Claim inventory
| Claim | Type | Source URL | Section | Provenance | Proof required? |
|---|---|---|---|---|---|
|  | benefit / mechanism / superiority / social proof / guarantee | | | observed / inferred | yes / no |

## 4. Proof inventory
| Proof item | Class | Exact wording / value | Source URL | Section | Notes |
|---|---|---|---|---|---|
|  | testimonial / stat / review count / logo / press / guarantee | verified_source / derived_source / missing | | | | |

## 5. CTA inventory
| CTA text | Destination guess | Source URL | Above fold? | Notes |
|---|---|---|---|---|

## 6. Mechanism language inventory
- Unique mechanism phrases repeated by the brand
- Product explanation phrases worth preserving
- Failed-alternative language
- Objection-handling language

## 7. Trust cue inventory
- guarantees
- shipping / returns / warranty
- certifications / press / logos
- compliance / safety / authority cues
- category conventions that signal legitimacy

## 8. Page pattern inventory
| Section order | What appears | What it is doing | Worth preserving? |
|---|---|---|---|

## 9. Visual motif inventory
- dominant colors
- font families / classes
- product photography style
- UI / screenshot style if present
- shape language
- density / spacing feel
- trust-critical design conventions

## 10. Audience signals
- who this appears to target
- awareness stage clues
- sophistication clues
- explicit pain language
- explicit desire language

## 11. Missing / weak areas
- missing mechanism details
- unsupported claims
- thin proof
- inaccessible pages
- anything requiring operator decision
```

## JSON contract

`extract.json` must include machine-readable keys for:
- `brand`
- `category`
- `offer`
- `hero_language`
- `claims[]`
- `proof_inventory[]`
- `cta_inventory[]`
- `mechanism_language[]`
- `trust_cues[]`
- `page_patterns[]`
- `visual_motifs[]`
- `audience_signals[]`
- `missing_flags[]`
- `confidence`

## Deep mode

When `--deep` is used:
1. scrape homepage
2. scrape one product / service page
3. scrape one proof-heavy page if available
4. scrape pricing, FAQ, or about page if available
5. merge findings with source URLs attached to every artifact

Default deep priority:
- product page
- reviews / testimonials page
- FAQ / pricing page
- about page

## Fallback behavior

If Firecrawl or scraping fails:
- capture whatever is accessible
- mark blocked sections explicitly
- request operator-provided screenshots or copy for missing trust/proof/mechanism data
- do not fabricate extracted structure as if it were observed

## Stop / continue logic

Continue if:
- offer is identifiable
- CTA is inferable
- at least some proof or trust cues are extractable

Downgrade if:
- proof is weak
- visual identity is partial
- category conventions are unclear

Stop and raise operator if:
- unique mechanism cannot be identified
- source is too thin to separate real claims from marketing fog
- regulated claims appear without clear proof

## Hand-off

After extraction, run `/page-strategy`.

Do not jump straight to copy unless the strategy artifact already exists.