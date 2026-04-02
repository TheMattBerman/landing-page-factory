#!/usr/bin/env python3
import argparse
import json
from copy import deepcopy
from pathlib import Path


def load_json(path: Path):
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def choose_first(images: list[dict], *, section_contains=None, preservation_class=None):
    for image in images:
        if section_contains and section_contains not in (image.get("section") or "").lower():
            continue
        if preservation_class and image.get("preservation_class") != preservation_class:
            continue
        return image
    return None


def choose_mechanism_image(images: list[dict]):
    for image in images:
        section = (image.get("section") or "").lower()
        if "mechanism" in section or "how-it-works" in section:
            return image
    for preservation_class in ("exact_product", "concept_support", "branded_environment"):
        image = choose_first(images, preservation_class=preservation_class)
        if image:
            return image
    return None


def choose_lifestyle_image(images: list[dict]):
    for image in images:
        if image.get("preservation_class") == "branded_environment":
            return image
    for image in images:
        shot_id = (image.get("shot_id") or "").lower()
        if "lifestyle" in shot_id:
            return image
    return None


def normalize_images_used(images: list[dict]) -> list[dict]:
    normalized = []
    for image in images:
        normalized.append(
            {
                "shot_id": image.get("shot_id"),
                "section": image.get("section"),
                "class": image.get("preservation_class"),
                "provider": image.get("provider"),
                "path": image.get("path"),
                "fallback": image.get("fallback", {}),
            }
        )
    return normalized


def merge_meta(base_meta: dict, resolved_assets: dict) -> dict:
    meta = deepcopy(base_meta)
    images = resolved_assets.get("images_used", [])

    hero_image = resolved_assets.get("hero_image")
    mechanism_image = choose_mechanism_image(images)
    lifestyle_image = choose_lifestyle_image(images)
    og_image = hero_image or mechanism_image or lifestyle_image or (images[0] if images else None)

    meta["image_provider_policy"] = resolved_assets.get("image_provider_policy", {})
    meta["hero_image"] = hero_image
    meta["mechanism_image"] = mechanism_image
    meta["lifestyle_image"] = lifestyle_image
    meta["og_image"] = og_image
    meta["image_slots"] = {
        "hero": hero_image,
        "mechanism": mechanism_image,
        "lifestyle": lifestyle_image,
        "og": og_image,
    }
    meta["images_used"] = normalize_images_used(images)
    meta["visual_manifest_present"] = resolved_assets.get("visual_manifest_present", False)

    review_flags = meta.get("review_flags", [])
    if any(image.get("fallback", {}).get("attempted") for image in images):
        if "One or more visuals used provider fallback." not in review_flags:
            review_flags.append("One or more visuals used provider fallback.")
    meta["review_flags"] = review_flags

    return meta


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--page-name")
    parser.add_argument("--page-dir")
    parser.add_argument("--base-meta")
    parser.add_argument("--resolved-assets")
    parser.add_argument("--output")
    args = parser.parse_args()

    if not args.page_dir and not args.page_name:
        raise SystemExit("Provide --page-dir or --page-name")

    if args.page_dir:
        page_dir = Path(args.page_dir).resolve()
    else:
        page_dir = (Path.cwd() / "workspace" / "pages" / args.page_name).resolve()

    base_meta_path = Path(args.base_meta).resolve() if args.base_meta else page_dir / "meta.json"
    resolved_assets_path = Path(args.resolved_assets).resolve() if args.resolved_assets else page_dir / "resolved-visuals.json"

    base_meta = load_json(base_meta_path)
    resolved_assets = load_json(resolved_assets_path)
    if not resolved_assets:
        raise SystemExit(f"Resolved assets file missing or empty: {resolved_assets_path}")

    merged = merge_meta(base_meta, resolved_assets)

    if args.output:
      out = Path(args.output)
    else:
      out = page_dir / "meta.json"

    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        json.dump(merged, fh, indent=2)
        fh.write("\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
