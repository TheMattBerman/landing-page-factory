#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def load_json(path: Path):
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def choose_first(images: list[dict], predicate):
    for image in images:
        if predicate(image):
            return image
    return None


def choose_slots(meta: dict) -> dict:
    images = meta.get("images_used", [])
    hero = meta.get("hero_image") or choose_first(images, lambda image: "hero" in (image.get("section") or "").lower() or "hero" in (image.get("shot_id") or "").lower())
    mechanism = meta.get("mechanism_image") or choose_first(images, lambda image: "mechanism" in (image.get("section") or "").lower() or "how-it-works" in (image.get("section") or "").lower())
    lifestyle = meta.get("lifestyle_image") or choose_first(images, lambda image: image.get("class") == "branded_environment" or "lifestyle" in (image.get("shot_id") or "").lower())

    og = hero or mechanism or lifestyle or (images[0] if images else None)

    return {
        "hero": hero,
        "mechanism": mechanism,
        "lifestyle": lifestyle,
        "og": og,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--meta", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()

    meta_path = Path(args.meta).resolve()
    meta = load_json(meta_path)
    slots = choose_slots(meta)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8") as fh:
            json.dump(slots, fh, indent=2)
            fh.write("\n")
    else:
        print(json.dumps(slots, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
