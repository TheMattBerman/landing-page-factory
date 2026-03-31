# Landing Page Factory — Eval Rubric

Central quality scoring system. Referenced by `page-copy`, `page-visuals`, `page-build`, and `page-qa`.

Every generated page is scored against these dimensions. Scores determine whether a page is shippable, draft-only, or blocked.

---

## Copy Evals

Scored during the `page-copy` sharpness audit.

| Dimension | Range | Pass | What It Measures |
|---|---:|---:|---|
| mechanism clarity | 1-10 | 8 | Does the page explain WHY the product works? |
| specificity | 1-10 | 8 | Concrete details vs. vague claims |
| proof density | 1-10 | 7 | Amount and quality of traceable evidence |
| objection coverage | 1-10 | 7 | Are real buyer blockers addressed? |
| phrase originality | 1-10 | 7 | Source language preserved vs. AI slop substituted |
| section discipline | 1-10 | 8 | One job per section, no drift |
| CTA clarity | 1-10 | 8 | Clear, specific next action |

**Copy composite** = average of all 7 dimensions.

---

## Visual Evals

Scored during `page-visuals` generation. Not all dimensions apply to every image — score only those relevant to the preservation class.

| Dimension | Range | Pass | Applies When |
|---|---:|---:|---|
| section-fit | 1-10 | 8 | Always — does the image serve its section's job? |
| palette fidelity | 1-10 | 8 | Always — matches brand color system |
| silhouette fidelity | 1-10 | 8 | Exact product preservation class |
| material fidelity | 1-10 | 8 | Exact product preservation class |
| packaging/UI fidelity | 1-10 | 8 | When packaging or UI is trust-critical |
| composition clarity | 1-10 | 8 | Always — clear focal point, readable layout |
| artifact absence | 1-10 | 9 | Always — no AI generation artifacts |
| text artifact absence | 1-10 | 10 | Always — zero garbled or hallucinated text |

**Visual composite** = average of applicable dimensions.

Reject and regenerate if any applicable dimension falls below its threshold.

---

## Build Evals

Scored during `page-build` post-build QA. Binary pass/fail — these are non-negotiable.

| Check | Type | What It Measures |
|---|---|---|
| mechanism visible above fold | pass/fail | Visitor understands the mechanism without scrolling |
| primary proof above fold | pass/fail | Trust signal visible immediately |
| CTA above fold | pass/fail | Action available without scrolling |
| trust cue above fold | pass/fail | Category-appropriate trust signal present |
| no invented proof | pass/fail | All proof items carry provenance tags |
| no banned slop patterns | pass/fail | Anti-slop checklist passes |
| mobile collapse checked | pass/fail | Responsive at 768px and 1024px breakpoints |
| contrast checked | pass/fail | WCAG AA minimum contrast ratios |
| alt text present | pass/fail | All images have descriptive alt text |
| category convention preserved | pass/fail | Trust-critical design patterns intact |

**Build pass** = all checks pass. Any failure = build is incomplete.

---

## Page-Level QA (Final Gate)

Scored during `page-qa`. This is the aggregate assessment across all stages.

| Dimension | Range | Pass | What It Measures |
|---|---:|---:|---|
| mechanism preservation | 1-10 | 8 | Did build/design weaken the mechanism? |
| proof discipline | 1-10 | 9 | Is all proof traceable and correctly tagged? |
| trust cue preservation | 1-10 | 8 | Are category trust conventions intact? |
| copy sharpness | 1-10 | 8 | Overall copy quality (from copy eval composite) |
| visual fidelity | 1-10 | 8 | Images serve the page correctly (from visual eval composite) |
| build quality | 1-10 | 8 | HTML/CSS/responsive quality |
| anti-slop compliance | 1-10 | 8 | No banned patterns, no generic AI design dialect |

---

## Verdict Logic

### Shippable
All hard thresholds pass. All proof is `verified_source` or `derived_source`. No review flags unresolved.

### Draft Only
Structure is good but gaps remain:
- Some proof items are `placeholder_draft`
- Visual assets are partial or placeholder
- Compliance review still required
- Some QA dimensions below threshold but fixable

### Blocked
Critical failures that prevent shipping:
- Proof is invented or untraceable in a way that affects conversion claims
- Mechanism is unclear or was weakened by design
- CTA path is broken or destination unknown
- Critical accessibility or rendering issues
- Compliance-sensitive claims without supporting proof

---

## Ranking Criteria (Comparing Variants)

When building multiple page variants for the same brand, rank by weighted composite:

| Priority | Dimension | Weight | Why |
|---:|---|---:|---|
| 1 | mechanism clarity | 25% | The core reason the page converts |
| 2 | proof discipline | 20% | Trust is non-negotiable |
| 3 | copy sharpness composite | 20% | Words do the selling |
| 4 | visual fidelity composite | 15% | Images support the mechanism |
| 5 | anti-slop compliance | 10% | Differentiation from generic AI output |
| 6 | build quality | 10% | Technical execution |

**Overall score** = weighted average of dimension composites.

Use this ranking to:
- Choose the best variant for a given audience/angle
- Identify which variant needs the most improvement
- Track quality across batch generation runs

---

## Eval Output Format

Every page package includes scores in `meta.json` and human-readable detail in `qa.md`.

### meta.json eval block
```json
{
  "eval": {
    "copy_composite": 8.3,
    "visual_composite": 8.5,
    "build_pass": true,
    "qa_composite": 8.4,
    "overall": 8.4,
    "verdict": "shippable"
  }
}
```

### qa.md format
Full dimension-by-dimension scoring with notes, hard fails, required fixes, and verdict.
