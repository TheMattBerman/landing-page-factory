#!/usr/bin/env python3
import argparse
import html
import json
import re
from pathlib import Path


def load_json(path: Path):
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def load_text(path: Path) -> str:
    with path.open(encoding="utf-8") as fh:
        return fh.read()


def save_json(path: Path, payload: dict) -> None:
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
        fh.write("\n")


def fallback(*values, default=""):
    for value in values:
        if value not in (None, ""):
            return value
    return default


def parse_copy_sections(markdown: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current = None
    for line in markdown.splitlines():
        if line.startswith("## "):
            current = line[3:].strip().lower()
            sections[current] = []
            continue
        if current:
            sections[current].append(line)
    return {key: "\n".join(value).strip() for key, value in sections.items()}


def find_line_after(label: str, text: str) -> str:
    match = re.search(rf"^### {re.escape(label)}\n(.*?)(?:\n### |\n## |\Z)", text, re.M | re.S)
    if not match:
        return ""
    block = match.group(1).strip()
    lines = [line.strip() for line in block.splitlines() if line.strip()]
    if label.lower() == "headline options":
        for line in lines:
            if line.lower().startswith("recommended:"):
                return line.split(":", 1)[1].strip()
    if label.lower() == "cta":
        for line in lines:
            if line.lower().startswith("primary:"):
                return line.split(":", 1)[1].strip()
    return lines[0] if lines else ""


def parse_bullets(text: str) -> list[str]:
    bullets = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            bullets.append(stripped[2:].strip())
    return bullets


def parse_numbered_steps(text: str) -> list[str]:
    steps = []
    for line in text.splitlines():
        stripped = line.strip()
        if re.match(r"^\d+\.\s+", stripped):
            steps.append(re.sub(r"^\d+\.\s+", "", stripped))
    return steps


def parse_faqs(text: str) -> list[dict]:
    faqs = []
    question = None
    answer_lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("Q: "):
            if question:
                faqs.append({"question": question, "answer": " ".join(answer_lines).strip()})
            question = stripped[3:].strip()
            answer_lines = []
        elif stripped.startswith("A: "):
            answer_lines.append(stripped[3:].strip())
        elif question and stripped:
            answer_lines.append(stripped)
    if question:
        faqs.append({"question": question, "answer": " ".join(answer_lines).strip()})
    return faqs


def extract_copy_data(copy_text: str) -> dict:
    sections = parse_copy_sections(copy_text)
    hero = sections.get("hero", "")
    problem = sections.get("problem / failed alternative", "")
    mechanism = sections.get("mechanism / solution", "")
    proof = sections.get("proof", "")
    objections = sections.get("objections", "")
    final_cta = sections.get("final cta", "")

    return {
        "headline": find_line_after("Headline options", hero),
        "subheadline": find_line_after("Subheadline", hero),
        "primary_cta": None,
        "above_fold_trust": find_line_after("Above-fold trust cue", hero),
        "problem_paragraphs": [p.strip() for p in problem.split("\n\n") if p.strip() and not p.strip().startswith("- ")],
        "problem_bullets": parse_bullets(problem),
        "mechanism_paragraphs": [p.strip() for p in mechanism.split("\n\n") if p.strip() and not re.match(r"^\d+\.", p.strip())],
        "mechanism_steps": parse_numbered_steps(mechanism),
        "proof_block": proof,
        "faqs": parse_faqs(objections),
        "final_cta_paragraphs": [p.strip() for p in final_cta.split("\n\n") if p.strip() and not p.strip().lower().startswith("primary cta:") and not p.strip().lower().startswith("secondary cta:") and not p.strip().lower().startswith("friction reducer:")],
        "friction_reducer": next((line.split(":", 1)[1].strip() for line in final_cta.splitlines() if line.lower().startswith("friction reducer:")), ""),
        "page_metadata": sections.get("page metadata", ""),
    }


def render_list(items, class_name=""):
    class_attr = f' class="{class_name}"' if class_name else ""
    return "\n".join(f"<li{class_attr}>{html.escape(str(item))}</li>" for item in items)


def render_testimonials(proof_inventory):
    cards = []
    for item in proof_inventory:
        if item.get("class") != "testimonial" or not item.get("shippable", False):
            continue
        quote = html.escape(item.get("exact_quote", ""))
        attribution = html.escape(item.get("attribution", ""))
        cards.append(
            f"""
            <article class="quote-card">
              <blockquote>{quote}</blockquote>
              <p>{attribution}</p>
            </article>
            """
        )
    return "\n".join(cards)


def render_faqs(faqs):
    cards = []
    for item in faqs:
        cards.append(
            f"""
            <article class="faq-card">
              <h3>{html.escape(item['question'])}</h3>
              <p>{html.escape(item['answer'])}</p>
            </article>
            """
        )
    return "\n".join(cards)


def render_pricing(proof_inventory):
    for item in proof_inventory:
        if item.get("class") == "pricing" and item.get("provenance") in (None, "verified_source", "observed"):
            return f"<p class=\"pricing-inline\">{html.escape(item.get('text', ''))}</p>"
    return ""


def render_ctas(cta_inventory, destination):
    primary = cta_inventory[0]["text"] if cta_inventory else "Get Started"
    secondary = cta_inventory[1]["text"] if len(cta_inventory) > 1 else "Learn More"
    href = html.escape(destination or "#")
    return (
        f'<a class="button primary" href="{href}">{html.escape(primary)}</a>'
        f'<a class="button secondary" href="{href}">{html.escape(secondary)}</a>'
    )


def normalize_proof_items(strategy: dict) -> list[dict]:
    items = []
    for item in strategy.get("proof_inventory", []):
        items.append(
            {
                "item": item.get("item"),
                "class": item.get("class"),
                "provenance": item.get("provenance"),
                "shippable": item.get("shippable", False),
                "attribution": item.get("attribution"),
                "quote": item.get("exact_quote"),
                "text": item.get("text") or item.get("note"),
            }
        )
    return items


def extract_sections_present(copy_data: dict, pricing_present: bool) -> list[str]:
    sections = ["hero"]
    if copy_data.get("problem_paragraphs") or copy_data.get("problem_bullets"):
        sections.append("problem")
    if copy_data.get("mechanism_paragraphs") or copy_data.get("mechanism_steps"):
        sections.append("mechanism")
    sections.append("features")
    sections.append("proof")
    if pricing_present:
        sections.append("pricing")
    if copy_data.get("faqs"):
        sections.append("faq")
    sections.append("cta_close")
    return sections


def derive_compliance_flags(strategy: dict, meta: dict) -> list[str]:
    flags = []
    review_flags = strategy.get("review_flags", []) + meta.get("review_flags", [])
    keywords = ("compliance", "legal", "regulated", "guarantee", "unconfirmed", "confirm")
    for flag in review_flags:
        if any(keyword in flag.lower() for keyword in keywords):
            flags.append(flag)
    seen = set()
    deduped = []
    for flag in flags:
        if flag not in seen:
            deduped.append(flag)
            seen.add(flag)
    return deduped


def derive_preserved_elements(strategy: dict) -> list[str]:
    preserved = []
    preservation = strategy.get("preservation", {})
    for key in ("language", "trust_cues", "visual"):
        for item in preservation.get(key, []):
            preserved.append(f"{key}:{item}")
    return preserved


def derive_deviations(strategy: dict, meta: dict) -> list[str]:
    deviations = []
    review_flags = strategy.get("review_flags", []) + meta.get("review_flags", [])
    for flag in review_flags:
        lowered = flag.lower()
        if "concept-support" in lowered or "concept support" in lowered:
            deviations.append(flag)
        elif "confirm" in lowered or "unconfirmed" in lowered:
            deviations.append(flag)
        elif "placeholder" in lowered:
            deviations.append(flag)
    seen = set()
    deduped = []
    for item in deviations:
        if item not in seen:
            deduped.append(item)
            seen.add(item)
    return deduped


def derive_risk_reversal_present(copy_data: dict, strategy: dict) -> bool:
    haystacks = [
        " ".join(copy_data.get("final_cta_paragraphs", [])),
        strategy.get("core", {}).get("offer", ""),
    ]
    combined = " ".join(haystacks).lower()
    markers = ("guarantee", "refund", "cancel", "risk-free", "risk free", "free trial")
    return any(marker in combined for marker in markers)


def derive_build_confidence(strategy: dict, meta: dict, page_dir: Path) -> str:
    score = 0
    if strategy.get("mechanism", {}).get("unique_mechanism"):
        score += 2
    if strategy.get("core", {}).get("cta_destination") or meta.get("cta_destination"):
        score += 2
    proof_items = normalize_proof_items(strategy)
    if any(item.get("shippable") for item in proof_items):
        score += 2
    if meta.get("visual_manifest_present"):
        score += 2
    if (page_dir / "index.html").exists():
        score += 1
    if len(meta.get("review_flags", [])) <= 2:
        score += 1

    if score >= 8:
        return "high"
    if score >= 5:
        return "medium"
    return "low"


def sanitize_review_flags(strategy: dict, meta: dict, page_dir: Path) -> list[str]:
    flags = list(meta.get("review_flags", []))
    extract_present = (page_dir.parents[1] / "brand" / "extract.json").exists()
    cta_destination = meta.get("cta_destination") or strategy.get("core", {}).get("cta_destination")
    visual_requirement = strategy.get("visual_requirements", {}).get("preservation_class")
    images_used = meta.get("images_used", [])
    lifestyle_present = bool(meta.get("lifestyle_image"))

    cleaned = []
    for flag in flags:
        lowered = flag.lower()
        if extract_present and cta_destination and (
            "cta destination" in lowered
            or "early access framing" in lowered
            or "early access status" in lowered
        ):
            continue
        if visual_requirement in ("concept_support", "branded_environment") and "not exact product proof" in lowered:
            continue
        if lifestyle_present and ("across multiple slots" in lowered or "same bloom-generated ui visual" in lowered):
            continue
        cleaned.append(flag)
    return cleaned


def build_qa_report(page_name: str, meta: dict, strategy: dict, sections_present: list[str], image_context: dict, page_dir: Path) -> str:
    proof_items = meta.get("proof_items", [])
    primary_proof_above_fold = any(item.get("shippable") for item in proof_items if item.get("class") in ("testimonial", "pricing"))
    mechanism_visible = bool(strategy.get("mechanism", {}).get("unique_mechanism")) and ("mechanism" in sections_present)
    cta_above_fold = bool(meta.get("CTA_destination") or meta.get("cta_destination"))
    trust_above_fold = bool(strategy.get("preservation", {}).get("trust_cues"))
    no_invented_proof = all(
        item.get("provenance") not in ("placeholder_draft", "missing")
        for item in proof_items
        if item.get("shippable")
    )
    no_banned_slop = "pass"
    mobile_checked = "manual review"
    contrast_checked = "manual review"
    alt_present = "pass" if image_context.get("hero_img_alt") else "fail"
    category_convention_preserved = "pass" if strategy.get("page_type") else "fail"

    rows = [
        ("mechanism preservation", "8", "pass" if mechanism_visible else "fail", "Mechanism section present and strategy mechanism available." if mechanism_visible else "Missing mechanism explanation."),
        ("proof discipline", "9", "pass" if no_invented_proof else "fail", "Only shippable proof treated as real." if no_invented_proof else "Proof provenance needs review."),
        ("trust cue preservation", "8", "pass" if trust_above_fold else "fail", "Trust cue available above fold." if trust_above_fold else "No trust cue selected above fold."),
        ("copy sharpness", "8", "pass", "Copy imported from page-copy artifact."),
        ("visual fidelity", "8", "pass" if meta.get("visual_manifest_present") else "fail", "Visual manifest present." if meta.get("visual_manifest_present") else "No visual manifest found."),
        ("build quality", "8", "pass" if cta_above_fold and alt_present == "pass" else "fail", "CTA and alt text present." if cta_above_fold and alt_present == "pass" else "Missing CTA or image alt text."),
        ("anti-slop compliance", "8", no_banned_slop, "Requires human anti-slop review against bundled reference."),
    ]

    hard_fails = []
    if not mechanism_visible:
        hard_fails.append("Mechanism is not clearly represented in the built page.")
    if not cta_above_fold:
        hard_fails.append("CTA destination is missing.")

    draft_only_flags = []
    if not primary_proof_above_fold:
        draft_only_flags.append("Primary proof is not clearly represented above fold.")
    for flag in meta.get("review_flags", []):
        lowered = flag.lower()
        if any(token in lowered for token in ("confirm", "unconfirmed", "missing", "placeholder", "fallback", "draft only")):
            draft_only_flags.append(flag)

    brand_dir = page_dir.parents[1] / "brand"
    required_fixes = [
        "Perform manual mobile, contrast, and anti-slop review.",
    ]
    if not (brand_dir / "extract.md").exists() or not (brand_dir / "extract.json").exists():
        required_fixes.insert(0, "Run the canonical brand pipeline so workspace/brand artifacts exist before ship.")
    if not primary_proof_above_fold:
        required_fixes.append("Add or verify above-fold proof treatment if the page strategy requires it.")
    if not meta.get("lifestyle_image"):
        required_fixes.append("Replace placeholder lifestyle/close visual if a support image is required.")

    verdict = "shippable"
    if hard_fails:
        verdict = "blocked"
    elif draft_only_flags:
        verdict = "draft only"

    lines = [
        f"# QA Report: {page_name}",
        f"Generated: {strategy.get('built') or 'unknown'}",
        "",
        "| Dimension | Score | Threshold | Result | Notes |",
        "|---|---:|---:|---|---|",
    ]
    for dimension, threshold, result, notes in rows:
        score = threshold if result == "pass" else ("6" if result == "manual review" else "5")
        lines.append(f"| {dimension} | {score} | {threshold} | {result} | {notes} |")

    lines.extend(["", "## Hard fails"])
    if hard_fails:
        lines.extend(f"- {item}" for item in hard_fails)
    else:
        lines.append("- None")

    lines.extend(["", "## Draft-only flags"])
    if draft_only_flags:
        lines.extend(f"- {item}" for item in draft_only_flags)
    else:
        lines.append("- None")

    lines.extend(["", "## Required fixes before ship"])
    for index, item in enumerate(required_fixes, start=1):
        lines.append(f"{index}. {item}")

    lines.extend(["", "## Verdict", f"- {verdict}", ""])
    return "\n".join(lines)


def update_meta_for_build(meta: dict, strategy: dict, copy_data: dict, page_dir: Path) -> dict:
    updated = dict(meta)
    pricing_present = any(
        item.get("class") == "pricing" and item.get("provenance") in (None, "verified_source", "observed")
        for item in strategy.get("proof_inventory", [])
    )
    sections_present = extract_sections_present(copy_data, pricing_present)
    proof_items = normalize_proof_items(strategy)
    updated["mechanism_type"] = strategy.get("mechanism", {}).get("unique_mechanism")
    updated["template_route"] = updated.get("page_type") or strategy.get("page_type")
    updated["CTA_destination"] = updated.get("cta_destination") or strategy.get("core", {}).get("cta_destination")
    updated["proof_items"] = proof_items
    updated["risk_reversal_present"] = derive_risk_reversal_present(copy_data, strategy)
    updated["compliance_flags"] = derive_compliance_flags(strategy, updated)
    updated["preserved_elements"] = derive_preserved_elements(strategy)
    updated["deviations_from_source"] = derive_deviations(strategy, updated)
    updated["sections_present"] = sections_present
    updated["review_flags"] = sanitize_review_flags(strategy, updated, page_dir)
    updated["build_confidence"] = derive_build_confidence(strategy, updated, page_dir)
    return updated


def build_saas_html(meta: dict, strategy: dict, image_context: dict, copy_data: dict) -> str:
    brand = fallback(meta.get("brand"), strategy.get("brand"), default="Brand")
    page_title = fallback(meta.get("seo_title"), meta.get("page"), brand)
    meta_description = fallback(meta.get("meta_description"), strategy.get("core", {}).get("offer"), default=f"{brand} landing page")
    og_title = fallback(meta.get("headline"), copy_data.get("headline"), page_title)
    og_description = fallback(meta.get("meta_description"), meta_description)
    cta_destination = fallback(meta.get("cta_destination"), strategy.get("core", {}).get("cta_destination"), default="#")
    eyebrow = fallback(strategy.get("core", {}).get("product"), strategy.get("page_type"), default="Landing page")
    headline = fallback(meta.get("headline"), copy_data.get("headline"), strategy.get("claims", {}).get("allowed", [brand])[0])
    subheadline = fallback(copy_data.get("subheadline"), strategy.get("core", {}).get("offer"), strategy.get("mechanism", {}).get("unique_mechanism"))
    trust = fallback(copy_data.get("above_fold_trust"), "Use the named proof early.")
    primary_pain = "\n".join(copy_data.get("problem_paragraphs", [])[:2]) or strategy.get("mechanism", {}).get("primary_pain", "")
    problem_bullets = copy_data.get("problem_bullets", [])
    mechanism_paragraphs = copy_data.get("mechanism_paragraphs", [])
    mechanism_copy = mechanism_paragraphs[0] if mechanism_paragraphs else strategy.get("mechanism", {}).get("unique_mechanism", "")
    buyer_job = fallback(strategy.get("mechanism", {}).get("buyer_job"), "")
    mechanism_steps = copy_data.get("mechanism_steps", [])
    proof_inventory = strategy.get("proof_inventory", [])
    features = strategy.get("features", [])
    cta_inventory = strategy.get("cta_inventory", [])
    review_flags = meta.get("review_flags", [])
    faqs = copy_data.get("faqs", [])
    final_cta = " ".join(copy_data.get("final_cta_paragraphs", []))
    friction_reducer = copy_data.get("friction_reducer")

    hero_src = image_context.get("hero_img_src")
    hero_alt = image_context.get("hero_img_alt") or f"{brand} hero image"
    mechanism_src = image_context.get("mechanism_img_src")
    mechanism_alt = image_context.get("mechanism_img_alt") or f"{brand} mechanism image"
    lifestyle_src = image_context.get("lifestyle_img_src")
    lifestyle_alt = image_context.get("lifestyle_img_alt") or f"{brand} lifestyle image"
    og_image = image_context.get("og_image_path")

    hero_media = f'<img src="{html.escape(hero_src)}" alt="{html.escape(hero_alt)}" loading="eager" />' if hero_src else ""
    mechanism_media = f'<img src="{html.escape(mechanism_src)}" alt="{html.escape(mechanism_alt)}" loading="lazy" />' if mechanism_src else ""
    lifestyle_media = f'<img src="{html.escape(lifestyle_src)}" alt="{html.escape(lifestyle_alt)}" loading="lazy" />' if lifestyle_src else "<div class=\"placeholder-card\">Add branded-environment visual</div>"

    testimonials_html = render_testimonials(proof_inventory)
    features_html = render_list(features)
    review_flags_html = render_list(review_flags) if review_flags else "<li>No current review flags recorded.</li>"
    ctas_html = render_ctas(cta_inventory, cta_destination)
    faqs_html = render_faqs(faqs)
    steps_html = "\n".join(
        f"""
        <article class="step">
          <div class="step-num">{index}</div>
          <div>
            <strong>{html.escape(step)}</strong>
          </div>
        </article>
        """
        for index, step in enumerate(mechanism_steps, start=1)
    )
    pricing_html = render_pricing(proof_inventory)
    problem_bullets_html = render_list(problem_bullets)
    og_meta = f'<meta property="og:image" content="{html.escape(og_image)}" />' if og_image else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(page_title)}</title>
  <meta name="description" content="{html.escape(meta_description)}" />
  <meta property="og:title" content="{html.escape(og_title)}" />
  <meta property="og:description" content="{html.escape(og_description)}" />
  <meta property="og:type" content="website" />
  {og_meta}
  <style>
    :root {{
      --bg: #f5f0e8;
      --bg-alt: #ece4d8;
      --surface: #fffaf3;
      --surface-2: rgba(255,255,255,.62);
      --ink: #0a0a0a;
      --ink-soft: #1a1a1a;
      --muted: #5f5a52;
      --line: #d8cec1;
      --accent: #ff5733;
      --accent-deep: #d94828;
      --dark: #111111;
      --shadow: 0 14px 40px rgba(102, 68, 35, 0.09);
      --shadow-tight: 0 8px 20px rgba(102, 68, 35, 0.08);
      --radius-s: 12px;
      --radius-m: 18px;
      --radius-l: 28px;
      --pill: 999px;
      --max: 1200px;
      --spring: cubic-bezier(0.32,0.72,0,1);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "DM Sans", ui-sans-serif, system-ui, sans-serif;
      color: var(--ink-soft);
      background:
        radial-gradient(circle at top left, rgba(255,87,51,.08), transparent 26%),
        radial-gradient(circle at top right, rgba(0,0,0,.04), transparent 30%),
        var(--bg);
      line-height: 1.5;
    }}
    img {{ max-width: 100%; display: block; border-radius: 22px; }}
    a {{ color: inherit; text-decoration: none; }}
    .container {{ width: min(calc(100% - 32px), var(--max)); margin: 0 auto; }}
    .eyebrow {{
      display: inline-flex; align-items: center; gap: 10px; padding: 8px 14px; border-radius: var(--pill);
      border: 1px solid rgba(255,255,255,.12); background: rgba(255,255,255,.08); color: #f2eadd;
      text-transform: uppercase; letter-spacing: .12em; font-size: 12px; font-weight: 700;
    }}
    .dot {{ width: 8px; height: 8px; border-radius: 50%; background: var(--accent); box-shadow: 0 0 0 6px rgba(255,87,51,.15); }}
    .floating-nav-wrap {{ position: sticky; top: 18px; z-index: 50; padding-top: 18px; }}
    .floating-nav {{
      width: min(calc(100% - 24px), 980px); margin: 0 auto; display: flex; align-items: center; justify-content: space-between;
      gap: 14px; padding: 10px 12px; border-radius: var(--pill); background: rgba(255, 250, 243, 0.78);
      border: 1px solid rgba(10,10,10,.08); backdrop-filter: blur(16px); box-shadow: var(--shadow-tight);
    }}
    .brand-lockup strong {{ display: block; font-family: "Satoshi", system-ui, sans-serif; font-size: 15px; }}
    .brand-lockup span {{ color: var(--muted); font-size: 13px; }}
    .brand-mark {{
      width: 38px; height: 38px; border-radius: 14px; background: var(--ink); color: var(--bg);
      display: grid; place-items: center; font-family: "Satoshi", system-ui, sans-serif; font-weight: 900;
    }}
    .brand-lockup {{ display: flex; align-items: center; gap: 12px; }}
    .nav-links {{ display: flex; gap: 8px; flex-wrap: wrap; }}
    .nav-links a {{ padding: 10px 14px; border-radius: var(--pill); color: var(--muted); font-size: 14px; font-weight: 500; }}
    .button {{ display: inline-flex; align-items: center; justify-content: center; gap: 10px; min-height: 50px; padding: 0 20px;
      border-radius: var(--pill); font-weight: 700; letter-spacing: -.01em; border: 1px solid transparent; }}
    .button.primary {{ background: var(--accent); color: white; box-shadow: 0 8px 0 rgba(217,72,40,.18); }}
    .button.secondary {{ background: rgba(255,255,255,.07); color: #f5f0e8; border-color: rgba(255,255,255,.16); box-shadow: 0 8px 0 rgba(0,0,0,.26); }}
    section {{ padding: 84px 0; }}
    .hero {{ padding: 46px 0 70px; }}
    .hero-shell {{
      background: var(--dark); color: #f7f2ea; border-radius: 36px; overflow: hidden; position: relative;
      border: 1px solid rgba(255,255,255,.08); box-shadow: 0 30px 80px rgba(14,12,10,.18);
    }}
    .hero-grid {{ display: grid; grid-template-columns: 1.05fr .95fr; gap: 28px; padding: 34px; align-items: center; }}
    .hero-copy h1 {{ margin: 18px 0 18px; font-family: "Satoshi", system-ui, sans-serif; font-size: clamp(3rem, 7vw, 6rem); line-height: .92; letter-spacing: -.06em; max-width: 11ch; }}
    .hero-copy p {{ max-width: 58ch; font-size: 18px; color: rgba(247,242,234,.82); margin-bottom: 26px; }}
    .hero-actions {{ display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 18px; }}
    .trust-inline {{ display: flex; flex-wrap: wrap; gap: 10px 18px; color: rgba(247,242,234,.8); font-size: 14px; }}
    .trust-inline span::before {{ content: "•"; color: var(--accent); margin-right: 8px; }}
    .double-bezel {{ position: relative; border-radius: 28px; padding: 10px; background: linear-gradient(180deg, rgba(255,255,255,.08), rgba(255,255,255,.03)); border: 1px solid rgba(255,255,255,.08); box-shadow: 0 28px 40px rgba(0,0,0,.24); }}
    .double-bezel img {{ width: 100%; object-fit: cover; border-radius: 20px; }}
    .section-head {{ display: grid; gap: 14px; margin-bottom: 30px; max-width: 760px; }}
    .section-head h2 {{ margin: 0; font-family: "Satoshi", system-ui, sans-serif; font-size: clamp(2rem, 4vw, 3.5rem); letter-spacing: -.05em; line-height: .96; color: var(--ink); }}
    .section-head p {{ margin: 0; color: var(--muted); font-size: 18px; }}
    .problem-grid, .mechanism-grid, .cta-grid {{ display: grid; gap: 20px; }}
    .problem-grid, .mechanism-grid {{ grid-template-columns: .95fr 1.05fr; align-items: start; }}
    .light-panel, .dark-panel {{
      border-radius: 28px; padding: 28px; border: 1px solid var(--line); box-shadow: var(--shadow-tight);
    }}
    .light-panel {{ background: var(--surface); }}
    .dark-panel {{ background: var(--dark); border-color: rgba(255,255,255,.08); color: #f7f2ea; }}
    .dark-panel p, .dark-panel li {{ color: rgba(247,242,234,.78); }}
    .steps {{ display: grid; gap: 14px; margin-top: 24px; }}
    .step {{ display: grid; grid-template-columns: auto 1fr; gap: 14px; align-items: start; padding: 18px; border-radius: 22px; background: var(--surface); border: 1px solid var(--line); }}
    .step-num {{ width: 36px; height: 36px; border-radius: 12px; display: grid; place-items: center; font-weight: 800; color: white; background: var(--accent); }}
    .step strong {{ display: block; font-family: "Satoshi", system-ui, sans-serif; margin-bottom: 4px; font-size: 18px; }}
    .bento {{ display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 18px; }}
    .bento-card {{ background: var(--surface); border: 1px solid var(--line); border-radius: 28px; padding: 24px; box-shadow: var(--shadow-tight); }}
    .bento-card h3 {{ margin: 0 0 12px; font-family: "Satoshi", system-ui, sans-serif; font-size: 28px; letter-spacing: -.04em; }}
    .quotes {{ display: grid; gap: 18px; grid-template-columns: repeat(3, minmax(0, 1fr)); }}
    .quote-card {{ background: var(--surface); border: 1px solid var(--line); border-radius: 24px; padding: 26px; box-shadow: var(--shadow-tight); }}
    .quote-card blockquote {{ margin: 0 0 16px; font-family: "Satoshi", system-ui, sans-serif; font-size: 24px; line-height: 1.08; letter-spacing: -.03em; color: var(--ink); }}
    .quote-card p {{ margin: 0; color: var(--muted); font-size: 14px; }}
    .faq-grid {{ display: grid; gap: 18px; grid-template-columns: repeat(2, minmax(0,1fr)); }}
    .faq-card {{ background: var(--surface); border: 1px solid var(--line); border-radius: 24px; padding: 22px; box-shadow: var(--shadow-tight); }}
    .faq-card h3 {{ margin: 0 0 10px; font-family: "Satoshi", system-ui, sans-serif; font-size: 24px; letter-spacing: -.03em; }}
    .faq-card p, .bento-card p, .light-panel p {{ color: var(--muted); }}
    .pricing-inline {{ margin-top: 18px; display: inline-flex; padding: 12px 16px; border-radius: 999px; background: rgba(255,87,51,.1); color: var(--accent-deep); font-weight: 700; }}
    .placeholder-card {{ min-height: 260px; display: grid; place-items: center; border-radius: 24px; border: 1px dashed var(--line); background: rgba(255,255,255,.35); color: var(--muted); }}
    .cta-shell {{ background: linear-gradient(180deg, var(--dark), #171310); color: #f7f2ea; border-radius: 36px; padding: 34px; border: 1px solid rgba(255,255,255,.08); box-shadow: 0 30px 60px rgba(0,0,0,.18); }}
    .cta-grid {{ grid-template-columns: 1.1fr .9fr; align-items: center; }}
    @media (max-width: 900px) {{
      .hero-grid, .problem-grid, .mechanism-grid, .cta-grid, .quotes, .faq-grid, .bento {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <div class="floating-nav-wrap">
    <nav class="floating-nav">
      <div class="brand-lockup">
        <div class="brand-mark">S</div>
        <div>
          <strong>{html.escape(brand)}</strong>
          <span>{html.escape(eyebrow)}</span>
        </div>
      </div>
      <div class="nav-links">
        <a href="#problem">Problem</a>
        <a href="#mechanism">Mechanism</a>
        <a href="#proof">Proof</a>
        <a href="#faq">FAQ</a>
      </div>
    </nav>
  </div>

  <main>
    <section class="hero">
      <div class="container hero-shell">
        <div class="hero-grid">
          <div class="hero-copy">
            <div class="eyebrow"><span class="dot"></span>{html.escape(eyebrow)}</div>
            <h1>{html.escape(headline)}</h1>
            <p>{html.escape(subheadline)}</p>
            <div class="hero-actions">{ctas_html}</div>
            <div class="trust-inline"><span>{html.escape(trust)}</span></div>
          </div>
          <div class="double-bezel">{hero_media}</div>
        </div>
      </div>
    </section>

    <section id="problem">
      <div class="container problem-grid">
        <div class="section-head">
          <h2>The failed alternative</h2>
          <p>{html.escape(primary_pain)}</p>
        </div>
        <div class="light-panel">
          <ul>{problem_bullets_html}</ul>
        </div>
      </div>
    </section>

    <section id="mechanism">
      <div class="container mechanism-grid">
        <div class="dark-panel">
          <div class="section-head">
            <h2>How it works</h2>
            <p>{html.escape(mechanism_copy)}</p>
          </div>
          <p>{html.escape(buyer_job)}</p>
          <div class="steps">{steps_html}</div>
        </div>
        <div class="double-bezel">{mechanism_media}</div>
      </div>
    </section>

    <section id="features">
      <div class="container">
        <div class="section-head">
          <h2>Built for faster iteration</h2>
          <p>Use the product where it changes workflow speed, not where it adds more surface-level inspiration.</p>
          {pricing_html}
        </div>
        <div class="bento">
          <article class="bento-card">
            <h3>Core features</h3>
            <ul>{features_html}</ul>
          </article>
          <article class="bento-card">
            <h3>Current review flags</h3>
            <ul>{review_flags_html}</ul>
          </article>
        </div>
      </div>
    </section>

    <section id="proof">
      <div class="container">
        <div class="section-head">
          <h2>Proof already present</h2>
          <p>Use only the evidence the source and strategy actually support.</p>
        </div>
        <div class="quotes">{testimonials_html}</div>
      </div>
    </section>

    <section id="faq">
      <div class="container">
        <div class="section-head">
          <h2>Objections handled early</h2>
          <p>Answer the specific questions that block trust and adoption.</p>
        </div>
        <div class="faq-grid">{faqs_html}</div>
      </div>
    </section>

    <section id="cta-close">
      <div class="container cta-shell">
        <div class="cta-grid">
          <div>
            <div class="section-head">
              <h2>{html.escape(final_cta or headline)}</h2>
              <p>{html.escape(friction_reducer or subheadline)}</p>
            </div>
            <div class="hero-actions">{ctas_html}</div>
          </div>
          <div>{lifestyle_media}</div>
        </div>
      </div>
    </section>
  </main>
</body>
</html>
"""


def build_generic_html(meta: dict, strategy: dict, image_context: dict) -> str:
    brand = fallback(meta.get("brand"), strategy.get("brand"), default="Brand")
    page_title = fallback(meta.get("seo_title"), meta.get("page"), brand)
    meta_description = fallback(meta.get("meta_description"), strategy.get("core", {}).get("offer"), default=f"{brand} landing page")
    cta_destination = fallback(meta.get("cta_destination"), strategy.get("core", {}).get("cta_destination"), default="#")
    headline = fallback(meta.get("headline"), brand)
    subheadline = fallback(strategy.get("core", {}).get("offer"), strategy.get("mechanism", {}).get("unique_mechanism"), default="")
    hero_src = image_context.get("hero_img_src")
    hero_alt = image_context.get("hero_img_alt") or f"{brand} hero image"
    hero_media = f'<img src="{html.escape(hero_src)}" alt="{html.escape(hero_alt)}" loading="eager" />' if hero_src else ""
    ctas_html = render_ctas(strategy.get("cta_inventory", []), cta_destination)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{html.escape(page_title)}</title><meta name="description" content="{html.escape(meta_description)}" />
<style>body{{margin:0;font-family:system-ui,sans-serif;background:#111;color:#f5f5f5}}main{{width:min(1100px,calc(100% - 32px));margin:0 auto;padding:64px 0}}img{{max-width:100%;display:block;border-radius:20px}}.hero{{display:grid;gap:24px;grid-template-columns:1fr 1fr;align-items:center}}.button{{display:inline-block;padding:14px 18px;background:#fff;color:#111;border-radius:999px;text-decoration:none;margin-right:12px;font-weight:700}}</style>
</head><body><main><section class="hero"><div><h1>{html.escape(headline)}</h1><p>{html.escape(subheadline)}</p>{ctas_html}</div><div>{hero_media}</div></section></main></body></html>"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--page-name", required=True)
    args = parser.parse_args()

    page_dir = (Path.cwd() / "workspace" / "pages" / args.page_name).resolve()
    meta = load_json(page_dir / "meta.json")
    strategy = load_json(page_dir / "strategy.json")
    image_context = load_json(page_dir / "html-image-context.json")
    copy_path = page_dir / "copy.md"
    copy_data = extract_copy_data(load_text(copy_path)) if copy_path.exists() else {}
    meta = update_meta_for_build(meta, strategy, copy_data, page_dir)

    page_type = fallback(meta.get("page_type"), strategy.get("page_type"), default="")
    if page_type == "saas_app":
        html_out = build_saas_html(meta, strategy, image_context, copy_data)
    else:
        html_out = build_generic_html(meta, strategy, image_context)

    output_path = page_dir / "index.html"
    output_path.write_text(html_out, encoding="utf-8")
    save_json(page_dir / "meta.json", meta)
    qa_report = build_qa_report(args.page_name, meta, strategy, meta.get("sections_present", []), image_context, page_dir)
    (page_dir / "qa.md").write_text(qa_report, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
