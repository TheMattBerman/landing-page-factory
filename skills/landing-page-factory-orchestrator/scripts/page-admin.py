#!/usr/bin/env python3
import argparse
import json
import re
from datetime import datetime
from pathlib import Path


def project_root() -> Path:
    for candidate in [Path.cwd(), *Path.cwd().parents]:
        if (candidate / "AGENTS.md").exists() and (candidate / "workspace").exists():
            return candidate
    raise SystemExit("Could not locate project root")


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value


def unique_page_name(base: str, pages_dir: Path) -> str:
    candidate = base
    counter = 2
    while (pages_dir / candidate).exists():
        candidate = f"{base}-{counter}"
        counter += 1
    return candidate


def load_json(path: Path):
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def load_text(path: Path) -> str | None:
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as fh:
        return fh.read()


def parse_qa_verdict(path: Path) -> str | None:
    text = load_text(path)
    if not text:
        return None
    match = re.search(r"^## Verdict\s*\n- ([^\n]+)", text, re.M)
    if match:
        return match.group(1).strip()
    return None


def brand_checks(root: Path) -> dict[str, Path]:
    return {
        "extract_md": root / "workspace" / "brand" / "extract.md",
        "extract_json": root / "workspace" / "brand" / "extract.json",
        "profile_md": root / "workspace" / "brand" / "profile.md",
        "palette_json": root / "workspace" / "brand" / "palette.json",
    }


def page_checks(page_dir: Path) -> dict[str, Path]:
    return {
        "strategy_json": page_dir / "strategy.json",
        "copy_md": page_dir / "copy.md",
        "visuals_dir": page_dir / "visuals",
        "visual_manifest": page_dir / "visuals" / "manifest.json",
        "index_html": page_dir / "index.html",
        "meta_json": page_dir / "meta.json",
        "qa_md": page_dir / "qa.md",
    }


def determine_next_stage(brand_state: dict[str, bool], page_state: dict[str, bool]) -> tuple[str | None, str | None]:
    if not brand_state["extract_md"] or not brand_state["extract_json"]:
        return "site-extract", "site-extract"
    if not page_state["strategy_json"]:
        return "page-strategy", "page-strategy"
    if not brand_state["profile_md"] or not brand_state["palette_json"]:
        return "brand-profile", "brand-profile"
    if not page_state["copy_md"]:
        return "page-copy", "page-copy"
    if not page_state["visuals_dir"]:
        return "page-visuals", "page-visuals"
    if not page_state["index_html"] or not page_state["meta_json"]:
        return "page-build", "page-build"
    if not page_state["qa_md"]:
        return "page-qa", "page-qa"
    return None, "complete"


def readiness_score(brand_state: dict[str, bool], page_state: dict[str, bool], qa_verdict: str | None) -> tuple[int, str]:
    score = 0

    brand_weights = {
        "extract_md": 15,
        "extract_json": 15,
        "profile_md": 15,
        "palette_json": 10,
    }
    page_weights = {
        "strategy_json": 10,
        "copy_md": 5,
        "visuals_dir": 5,
        "visual_manifest": 5,
        "index_html": 5,
        "meta_json": 5,
        "qa_md": 5,
    }

    for key, weight in brand_weights.items():
        if brand_state.get(key):
            score += weight
    for key, weight in page_weights.items():
        if page_state.get(key):
            score += weight

    verdict_bonus = {
        "shippable": 5,
        "draft only": 0,
        "draft-only": 0,
        "blocked": -10,
    }
    if qa_verdict:
        score += verdict_bonus.get(qa_verdict.lower(), 0)

    if qa_verdict:
        lowered = qa_verdict.lower()
        if lowered in ("draft only", "draft-only"):
            score = min(score, 89)
        elif lowered == "blocked":
            score = min(score, 59)

    if score >= 95:
        label = "ready"
    elif score >= 75:
        label = "near-ready"
    elif score >= 50:
        label = "in-progress"
    else:
        label = "early"

    return score, label


def strategic_adjustments(meta: dict, manifest: dict, qa_verdict: str | None) -> tuple[int, list[str]]:
    delta = 0
    notes: list[str] = []

    if meta.get("headline"):
        delta += 2
    else:
        notes.append("Missing headline metadata")

    if meta.get("cta_destination"):
        delta += 2
    else:
        notes.append("Missing CTA destination metadata")

    if meta.get("page_type"):
        delta += 1
    else:
        notes.append("Missing page type metadata")

    if meta.get("visual_manifest_present"):
        delta += 2
    else:
        notes.append("No visual manifest present")

    images_used = meta.get("images_used") or []
    if len(images_used) >= 2:
        delta += 2
    elif images_used:
        delta += 1
    else:
        notes.append("No build-resolved images recorded")

    fallback_attempted = any((image.get("fallback") or {}).get("attempted") for image in images_used)
    if fallback_attempted:
        delta -= 3
        notes.append("Provider fallback occurred")

    review_flags = meta.get("review_flags") or []
    if review_flags:
        delta -= min(len(review_flags), 4)
        notes.append(f"{len(review_flags)} review flag(s)")

    required_meta_keys = [
        "headline",
        "page_type",
        "cta_destination",
        "review_flags",
        "images_used",
        "visual_manifest_present",
    ]
    missing_required = [key for key in required_meta_keys if key not in meta]
    if missing_required:
        delta -= min(len(missing_required), 4)
        notes.append(f"Missing build metadata keys: {', '.join(missing_required)}")

    if qa_verdict and qa_verdict.lower() == "blocked":
        notes.append("QA verdict is blocked")

    return delta, notes


def page_status_payload(root: Path, page_name: str) -> dict:
    page_dir = root / "workspace" / "pages" / page_name
    brand_state = {name: path.exists() for name, path in brand_checks(root).items()}
    page_state = {name: path.exists() for name, path in page_checks(page_dir).items()}
    earliest_missing_stage, next_recommended_stage = determine_next_stage(brand_state, page_state)
    meta = load_json(page_dir / "meta.json") or {}
    strategy = load_json(page_dir / "strategy.json") or {}
    manifest = load_json(page_dir / "visuals" / "manifest.json") or {}
    qa_verdict = parse_qa_verdict(page_dir / "qa.md")
    score, label = readiness_score(brand_state, page_state, qa_verdict)
    strategic_delta, readiness_notes = strategic_adjustments(meta, manifest, qa_verdict)
    score = max(0, min(100, score + strategic_delta))
    if qa_verdict:
        lowered = qa_verdict.lower()
        if lowered in ("draft only", "draft-only"):
            score = min(score, 89)
        elif lowered == "blocked":
            score = min(score, 59)
    if score >= 95:
        label = "ready"
    elif score >= 75:
        label = "near-ready"
    elif score >= 50:
        label = "in-progress"
    else:
        label = "early"

    return {
        "page_name": page_name,
        "page_dir": str(page_dir),
        "exists": page_dir.exists(),
        "brand": brand_state,
        "page": page_state,
        "earliest_missing_stage": earliest_missing_stage,
        "next_recommended_stage": next_recommended_stage,
        "headline": meta.get("headline"),
        "page_type": meta.get("page_type") or strategy.get("page_type"),
        "cta_destination": meta.get("cta_destination") or strategy.get("core", {}).get("cta_destination"),
        "image_count": len(manifest.get("shots", [])) if manifest else None,
        "qa_verdict": qa_verdict,
        "readiness_score": score,
        "readiness_label": label,
        "readiness_notes": readiness_notes,
        "review_flags": meta.get("review_flags", []),
    }


def format_variant_markdown(payload: dict) -> str:
    lines = [f"# Variant Comparison ({payload['variant_count']})", ""]

    leader = payload["variants"][0] if payload["variants"] else None
    if leader:
        top_score = leader["readiness_score"]
        tied = [variant["page_name"] for variant in payload["variants"] if variant.get("readiness_score") == top_score]
        if len(tied) > 1:
            lines.extend([
                f"Tied top variants: {', '.join(f'`{name}`' for name in tied)} ({top_score}/100, {leader['readiness_label']})",
                "",
            ])
        else:
            lines.extend([
                f"Top ranked variant: `{leader['page_name']}` ({leader['readiness_score']}/100, {leader['readiness_label']})",
                "",
            ])

    lines.extend([
        "| Variant | Readiness | Headline | Page Type | Next Stage | QA Verdict | Images | CTA | Review Flags |",
        "|---|---:|---|---|---|---|---:|---|---|",
    ])

    for variant in payload["variants"]:
        review_flags = "; ".join(variant.get("review_flags") or []) or "None"
        headline = variant.get("headline") or "—"
        page_type = variant.get("page_type") or "—"
        next_stage = variant.get("next_recommended_stage") or "—"
        qa_verdict = variant.get("qa_verdict") or "—"
        readiness = f"{variant.get('readiness_score', 0)}/100 ({variant.get('readiness_label', '—')})"
        image_count = variant.get("image_count")
        image_count_text = str(image_count) if image_count is not None else "—"
        cta = variant.get("cta_destination") or "—"
        lines.append(
            f"| `{variant['page_name']}` | {readiness} | {headline} | {page_type} | {next_stage} | {qa_verdict} | {image_count_text} | {cta} | {review_flags} |"
        )

    lines.extend(["", "## Artifact Status", ""])
    for variant in payload["variants"]:
        lines.append(f"### {variant['page_name']}")
        lines.append("")
        lines.append(f"- Readiness: `{variant.get('readiness_score', 0)}/100` ({variant.get('readiness_label', '—')})")
        lines.append(f"- Next recommended stage: `{variant.get('next_recommended_stage') or '—'}`")
        if variant.get("earliest_missing_stage"):
            lines.append(f"- Earliest missing stage: `{variant['earliest_missing_stage']}`")
        lines.append(f"- Brand artifacts present: {', '.join(name for name, present in variant['brand'].items() if present) or 'none'}")
        lines.append(f"- Page artifacts present: {', '.join(name for name, present in variant['page'].items() if present) or 'none'}")
        lines.append(f"- Readiness notes: {'; '.join(variant.get('readiness_notes') or []) or 'None'}")
        lines.append("")

    return "\n".join(lines)


def emit_output(text: str, output: str | None) -> None:
    if output:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text + ("" if text.endswith("\n") else "\n"), encoding="utf-8")
    else:
        print(text)


def suggest_name(args) -> int:
    root = project_root()
    pages_dir = root / "workspace" / "pages"
    parts = [slugify(args.brand)]
    if args.audience:
      parts.append(slugify(args.audience))
    if args.angle:
      parts.append(slugify(args.angle))
    if args.offer:
      parts.append(slugify(args.offer))

    base = "-".join(part for part in parts if part)
    if not base:
        raise SystemExit("Need at least one of --brand, --audience, --angle, or --offer")

    payload = {
        "base_name": base,
        "suggested_name": unique_page_name(base, pages_dir),
        "pages_dir": str(pages_dir),
    }
    print(json.dumps(payload, indent=2))
    return 0


def artifact_status(args) -> int:
    root = project_root()
    payload = page_status_payload(root, args.page_name)
    print(json.dumps(payload, indent=2))
    return 0


def compare_variants(args) -> int:
    root = project_root()
    pages_dir = root / "workspace" / "pages"

    page_names = list(args.page_name or [])
    if args.prefix:
        matches = sorted(
            path.name for path in pages_dir.iterdir()
            if path.is_dir() and path.name.startswith(args.prefix)
        )
        for match in matches:
            if match not in page_names:
                page_names.append(match)

    if not page_names:
        raise SystemExit("Provide --page-name at least once or use --prefix")

    variants = sorted(
        [page_status_payload(root, page_name) for page_name in page_names],
        key=lambda variant: (
            -variant.get("readiness_score", 0),
            -(1 if (variant.get("qa_verdict") or "").lower() == "shippable" else 0),
            len(variant.get("review_flags") or []),
            variant["page_name"],
        ),
    )
    payload = {
        "variant_count": len(variants),
        "variants": variants,
    }
    if args.format == "markdown":
        emit_output(format_variant_markdown(payload), args.output)
    else:
        text = json.dumps(payload, indent=2)
        emit_output(text, args.output)
    return 0


def log_memory(args) -> int:
    root = project_root()
    memory_dir = root / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    path = memory_dir / f"{today}.md"

    lines = [f"## {args.title}", ""]
    if args.page_name:
        lines.append(f"- Page: `{args.page_name}`")
    if args.brand:
        lines.append(f"- Brand: `{args.brand}`")
    if args.stages:
        lines.append(f"- Stages: {args.stages}")
    if args.verdict:
        lines.append(f"- Verdict: {args.verdict}")
    if args.notes:
        lines.append(f"- Notes: {args.notes}")
    lines.append("")

    with path.open("a", encoding="utf-8") as fh:
        fh.write("\n".join(lines))

    print(json.dumps({"logged_to": str(path), "title": args.title}, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    suggest = subparsers.add_parser("suggest-name")
    suggest.add_argument("--brand", default="")
    suggest.add_argument("--audience", default="")
    suggest.add_argument("--angle", default="")
    suggest.add_argument("--offer", default="")
    suggest.set_defaults(func=suggest_name)

    status = subparsers.add_parser("status")
    status.add_argument("--page-name", required=True)
    status.set_defaults(func=artifact_status)

    compare = subparsers.add_parser("compare-variants")
    compare.add_argument("--page-name", action="append")
    compare.add_argument("--prefix")
    compare.add_argument("--format", choices=["json", "markdown"], default="json")
    compare.add_argument("--output")
    compare.set_defaults(func=compare_variants)

    log = subparsers.add_parser("log-memory")
    log.add_argument("--title", required=True)
    log.add_argument("--page-name")
    log.add_argument("--brand")
    log.add_argument("--stages")
    log.add_argument("--verdict")
    log.add_argument("--notes")
    log.set_defaults(func=log_memory)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
