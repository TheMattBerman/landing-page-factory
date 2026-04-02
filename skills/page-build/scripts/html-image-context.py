#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def load_json(path: Path):
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def phrase_from_section(section: str | None, default: str) -> str:
    if not section:
        return default
    value = section.replace("_", " ").replace("-", " ").strip().lower()
    return value or default


def alt_for_slot(brand: str | None, slot_name: str, image: dict | None) -> str | None:
    if not image:
        return None

    brand_name = brand or "the brand"
    preservation_class = image.get("preservation_class") or image.get("class")
    section_phrase = phrase_from_section(image.get("section"), slot_name)

    if preservation_class == "exact_product":
        return f"{brand_name} product image supporting the {section_phrase} section"
    if preservation_class == "branded_environment":
        return f"Lifestyle image for {brand_name} supporting the {section_phrase} section"
    if preservation_class == "concept_support":
        return f"Illustrative image for {brand_name} supporting the {section_phrase} section"
    return f"Image for {brand_name} supporting the {section_phrase} section"


def slot_payload(brand: str | None, slot_name: str, image: dict | None) -> dict | None:
    if not image:
        return None
    return {
        "src": image.get("path"),
        "alt": alt_for_slot(brand, slot_name, image),
        "loading": "eager" if slot_name == "hero" else "lazy",
        "provider": image.get("provider"),
        "preservation_class": image.get("preservation_class") or image.get("class"),
    }


def build_context(meta: dict) -> dict:
    brand = meta.get("brand")
    slots = meta.get("image_slots", {})
    context = {
        "hero_img_src": None,
        "hero_img_alt": None,
        "mechanism_img_src": None,
        "mechanism_img_alt": None,
        "lifestyle_img_src": None,
        "lifestyle_img_alt": None,
        "og_image_path": None,
        "slots": {},
    }

    for slot_name in ("hero", "mechanism", "lifestyle", "og"):
        payload = slot_payload(brand, slot_name, slots.get(slot_name))
        context["slots"][slot_name] = payload

    if context["slots"]["hero"]:
        context["hero_img_src"] = context["slots"]["hero"]["src"]
        context["hero_img_alt"] = context["slots"]["hero"]["alt"]
    if context["slots"]["mechanism"]:
        context["mechanism_img_src"] = context["slots"]["mechanism"]["src"]
        context["mechanism_img_alt"] = context["slots"]["mechanism"]["alt"]
    if context["slots"]["lifestyle"]:
        context["lifestyle_img_src"] = context["slots"]["lifestyle"]["src"]
        context["lifestyle_img_alt"] = context["slots"]["lifestyle"]["alt"]
    if context["slots"]["og"]:
        context["og_image_path"] = context["slots"]["og"]["src"]

    return context


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--meta", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()

    meta = load_json(Path(args.meta).resolve())
    context = build_context(meta)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8") as fh:
            json.dump(context, fh, indent=2)
            fh.write("\n")
    else:
        print(json.dumps(context, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
