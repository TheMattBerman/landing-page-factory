#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}


def load_json(path: Path):
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def rel_to_page(path: Path, page_dir: Path) -> str:
    try:
        return str(path.relative_to(page_dir))
    except ValueError:
        return str(path)


def normalize_manifest_shots(page_dir: Path, manifest: dict) -> list[dict]:
    shots = []
    project_root = Path.cwd().resolve()
    for shot in manifest.get("shots", []):
        local_path_raw = shot.get("local_path")
        local_path = Path(local_path_raw) if local_path_raw else None
        if local_path and not local_path.is_absolute():
            if local_path.parts[:2] == ("workspace", "pages"):
                local_path = (project_root / local_path).resolve()
            else:
                local_path = (page_dir / local_path).resolve()

        rel_path = rel_to_page(local_path, page_dir) if local_path else None
        shots.append(
            {
                "shot_id": shot.get("shot_id"),
                "section": shot.get("section"),
                "preservation_class": shot.get("preservation_class"),
                "provider": shot.get("provider"),
                "status": shot.get("status"),
                "path": rel_path,
                "absolute_path": str(local_path) if local_path else None,
                "prompt": shot.get("prompt"),
                "brand_context_source": shot.get("brand_context_source"),
                "source_refs": shot.get("source_refs", []),
                "provider_metadata": shot.get("provider_metadata", {}),
                "fallback": shot.get("fallback", {}),
                "notes": shot.get("notes", []),
            }
        )
    return shots


def scan_visual_files(page_dir: Path) -> list[dict]:
    visuals_dir = page_dir / "visuals"
    shots = []
    if not visuals_dir.exists():
        return shots

    for path in sorted(visuals_dir.iterdir()):
        if not path.is_file() or path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        shots.append(
            {
                "shot_id": path.stem,
                "section": None,
                "preservation_class": None,
                "provider": None,
                "status": "completed",
                "path": rel_to_page(path, page_dir),
                "absolute_path": str(path.resolve()),
                "prompt": None,
                "brand_context_source": None,
                "source_refs": [],
                "provider_metadata": {},
                "fallback": {},
                "notes": [],
            }
        )
    return shots


def choose_hero(shots: list[dict]) -> dict | None:
    for shot in shots:
        if shot.get("section") and "hero" in shot["section"].lower():
            return shot
    for shot in shots:
        if shot.get("shot_id") and "hero" in shot["shot_id"].lower():
            return shot
    return shots[0] if shots else None


def build_payload(page_dir: Path) -> dict:
    manifest = load_json(page_dir / "visuals" / "manifest.json")
    if manifest:
        shots = normalize_manifest_shots(page_dir, manifest)
        policy = manifest.get("image_provider_policy", {})
    else:
        shots = scan_visual_files(page_dir)
        policy = {}

    completed_shots = [shot for shot in shots if shot.get("status") == "completed" and shot.get("path")]
    hero_shot = choose_hero(completed_shots)

    return {
        "page_name": page_dir.name,
        "visual_manifest_present": manifest is not None,
        "image_provider_policy": policy,
        "hero_image": hero_shot,
        "images_used": completed_shots,
        "image_count": len(completed_shots),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--page-name")
    parser.add_argument("--page-dir")
    parser.add_argument("--output")
    args = parser.parse_args()

    if not args.page_dir and not args.page_name:
        raise SystemExit("Provide --page-dir or --page-name")

    if args.page_dir:
        page_dir = Path(args.page_dir).resolve()
    else:
        page_dir = (Path.cwd() / "workspace" / "pages" / args.page_name).resolve()

    payload = build_payload(page_dir)
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
            fh.write("\n")
    else:
        print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
