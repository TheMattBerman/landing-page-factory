#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def load_json(path: Path):
    if not path.exists():
      return None
    with path.open(encoding="utf-8") as fh:
      return json.load(fh)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--policy-primary", required=True)
    parser.add_argument("--policy-fallback", default="")
    parser.add_argument("--shot-file", required=True)
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    shot_path = Path(args.shot_file)
    shot = load_json(shot_path)
    if shot is None:
        raise SystemExit("shot file missing")

    manifest = load_json(manifest_path) or {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "image_provider_policy": {
            "primary": args.policy_primary,
            "fallback": args.policy_fallback or None,
        },
        "shots": [],
    }

    manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
    manifest["page_name"] = shot["page_name"]
    manifest["image_provider_policy"] = {
        "primary": args.policy_primary,
        "fallback": args.policy_fallback or None,
    }

    shots = [entry for entry in manifest.get("shots", []) if entry.get("shot_id") != shot["shot_id"]]
    shots.append(shot)
    shots.sort(key=lambda entry: entry.get("shot_id", ""))
    manifest["shots"] = shots

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
