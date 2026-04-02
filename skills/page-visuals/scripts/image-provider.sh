#!/usr/bin/env bash
# shellcheck disable=SC2155
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

resolve_project_root() {
  if [[ -n "${LPF_ROOT:-}" ]]; then
    printf '%s\n' "$LPF_ROOT"
    return 0
  fi

  if [[ -d "$(pwd)/workspace" || -f "$(pwd)/AGENTS.md" ]]; then
    pwd
    return 0
  fi

  local candidate="$SCRIPT_DIR"
  while [[ "$candidate" != "/" ]]; do
    if [[ -d "$candidate/workspace" || -f "$candidate/AGENTS.md" ]]; then
      printf '%s\n' "$candidate"
      return 0
    fi
    candidate="$(dirname "$candidate")"
  done

  pwd
}

PROJECT_ROOT="$(resolve_project_root)"
MANIFEST_LIB="$PROJECT_ROOT/scripts/lib/update_visual_manifest.py"

usage() {
  cat <<'EOF'
Usage:
  bash skills/page-visuals/scripts/image-provider.sh \
    --page-name PAGE \
    --shot-id SHOT \
    --prompt PROMPT \
    --preservation-class CLASS \
    [--section SECTION] \
    [--aspect-ratio RATIO] \
    [--source-url URL] \
    [--brand-name NAME] \
    [--output PATH] \
    [--ref URL_OR_PATH]...

Environment:
  IMAGE_PROVIDER=bloom
  IMAGE_FALLBACK_PROVIDER=nano-banana
EOF
}

PAGE_NAME=""
SHOT_ID=""
PROMPT=""
PRESERVATION_CLASS=""
SECTION=""
ASPECT_RATIO="16:9"
SOURCE_URL=""
BRAND_NAME=""
OUTPUT_PATH=""
REFS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --page-name)
      PAGE_NAME="${2:-}"
      shift 2
      ;;
    --shot-id)
      SHOT_ID="${2:-}"
      shift 2
      ;;
    --prompt)
      PROMPT="${2:-}"
      shift 2
      ;;
    --preservation-class)
      PRESERVATION_CLASS="${2:-}"
      shift 2
      ;;
    --section)
      SECTION="${2:-}"
      shift 2
      ;;
    --aspect-ratio)
      ASPECT_RATIO="${2:-}"
      shift 2
      ;;
    --source-url)
      SOURCE_URL="${2:-}"
      shift 2
      ;;
    --brand-name)
      BRAND_NAME="${2:-}"
      shift 2
      ;;
    --output)
      OUTPUT_PATH="${2:-}"
      shift 2
      ;;
    --ref)
      REFS+=("${2:-}")
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ -z "$PAGE_NAME" || -z "$SHOT_ID" || -z "$PROMPT" || -z "$PRESERVATION_CLASS" ]]; then
  usage >&2
  exit 1
fi

VISUALS_DIR="$PROJECT_ROOT/workspace/pages/$PAGE_NAME/visuals"
mkdir -p "$VISUALS_DIR"

if [[ -z "$OUTPUT_PATH" ]]; then
  OUTPUT_PATH="$VISUALS_DIR/$SHOT_ID.jpg"
fi

PRIMARY_PROVIDER="${IMAGE_PROVIDER:-bloom}"
FALLBACK_PROVIDER="${IMAGE_FALLBACK_PROVIDER:-nano-banana}"
MANIFEST_PATH="$VISUALS_DIR/manifest.json"
TMP_DIR="$(mktemp -d)"
JOB_JSON="$TMP_DIR/job.json"
PRIMARY_RESULT="$TMP_DIR/primary.json"
FINAL_RESULT="$TMP_DIR/final.json"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

export PAGE_NAME SHOT_ID PROMPT PRESERVATION_CLASS SECTION ASPECT_RATIO SOURCE_URL BRAND_NAME OUTPUT_PATH PRIMARY_PROVIDER FALLBACK_PROVIDER
export REFS_RAW="$(printf '%s\n' "${REFS[@]-}")"
export REFS_JSON="$(python3 -c 'import json, os; raw = os.environ.get("REFS_RAW", ""); refs = [item for item in raw.split("\n") if item]; print(json.dumps(refs))')"

python3 - "$JOB_JSON" <<'PY'
import json
import os
import sys

path = sys.argv[1]
job = {
    "page_name": os.environ["PAGE_NAME"],
    "shot_id": os.environ["SHOT_ID"],
    "prompt": os.environ["PROMPT"],
    "preservation_class": os.environ["PRESERVATION_CLASS"],
    "section": os.environ.get("SECTION") or None,
    "aspect_ratio": os.environ["ASPECT_RATIO"],
    "source_url": os.environ.get("SOURCE_URL") or None,
    "brand_name": os.environ.get("BRAND_NAME") or None,
    "output_path": os.environ["OUTPUT_PATH"],
    "refs": json.loads(os.environ["REFS_JSON"]),
    "policy": {
        "primary": os.environ["PRIMARY_PROVIDER"],
        "fallback": os.environ.get("FALLBACK_PROVIDER") or None,
    },
}
with open(path, "w", encoding="utf-8") as fh:
    json.dump(job, fh, indent=2)
PY

run_provider() {
  local provider="$1"
  local output_json="$2"
  local provider_script="$SCRIPT_DIR/providers/$provider.sh"

  if [[ ! -x "$provider_script" ]]; then
    python3 - "$output_json" "$provider" <<'PY'
import json
import sys

path, provider = sys.argv[1:3]
payload = {
    "provider": provider,
    "status": "failed",
    "reason": f"Provider adapter missing: {provider}",
    "provider_metadata": {},
    "notes": [f"No executable adapter found for provider '{provider}'."],
}
with open(path, "w", encoding="utf-8") as fh:
    json.dump(payload, fh, indent=2)
PY
    return 10
  fi

  set +e
  "$provider_script" generate "$JOB_JSON" >"$output_json"
  local status=$?
  set -e
  return "$status"
}

merge_result() {
  local input_json="$1"
  local final_json="$2"
  local fallback_attempted="$3"
  local fallback_from="$4"
  local fallback_reason="$5"

  python3 - "$JOB_JSON" "$input_json" "$final_json" "$fallback_attempted" "$fallback_from" "$fallback_reason" <<'PY'
import json
import sys
from datetime import datetime, timezone

job_path, result_path, out_path, fallback_attempted, fallback_from, fallback_reason = sys.argv[1:7]
with open(job_path, encoding="utf-8") as fh:
    job = json.load(fh)
with open(result_path, encoding="utf-8") as fh:
    result = json.load(fh)

payload = {
    "shot_id": job["shot_id"],
    "page_name": job["page_name"],
    "section": job.get("section"),
    "preservation_class": job["preservation_class"],
    "prompt": job["prompt"],
    "aspect_ratio": job["aspect_ratio"],
    "provider": result.get("provider"),
    "status": result.get("status", "failed"),
    "local_path": result.get("local_path"),
    "brand_context_source": result.get("brand_context_source"),
    "source_refs": job.get("refs", []),
    "provider_metadata": result.get("provider_metadata", {}),
    "notes": result.get("notes", []),
    "reason": result.get("reason"),
    "fallback": {
        "attempted": fallback_attempted == "true",
        "from_provider": fallback_from or None,
        "reason": fallback_reason or None,
    },
    "attempted_at": datetime.now(timezone.utc).isoformat(),
}

with open(out_path, "w", encoding="utf-8") as fh:
    json.dump(payload, fh, indent=2)
PY
}

update_manifest() {
  python3 "$MANIFEST_LIB" \
    --manifest "$MANIFEST_PATH" \
    --policy-primary "$PRIMARY_PROVIDER" \
    --policy-fallback "$FALLBACK_PROVIDER" \
    --shot-file "$FINAL_RESULT"
}

PRIMARY_STATUS=0
PRIMARY_REASON=""

run_provider "$PRIMARY_PROVIDER" "$PRIMARY_RESULT" || PRIMARY_STATUS=$?

if [[ "$PRIMARY_STATUS" -eq 0 ]]; then
  merge_result "$PRIMARY_RESULT" "$FINAL_RESULT" "false" "" ""
  update_manifest
  python3 -m json.tool "$FINAL_RESULT"
  exit 0
fi

PRIMARY_REASON="$(python3 - "$PRIMARY_RESULT" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as fh:
    data = json.load(fh)
print(data.get("reason", "primary provider failed"))
PY
)"

if [[ -z "$FALLBACK_PROVIDER" || "$FALLBACK_PROVIDER" == "$PRIMARY_PROVIDER" ]]; then
  merge_result "$PRIMARY_RESULT" "$FINAL_RESULT" "false" "" ""
  update_manifest
  python3 -m json.tool "$FINAL_RESULT"
  exit "$PRIMARY_STATUS"
fi

FALLBACK_RESULT="$TMP_DIR/fallback.json"
FALLBACK_STATUS=0
run_provider "$FALLBACK_PROVIDER" "$FALLBACK_RESULT" || FALLBACK_STATUS=$?
merge_result "$FALLBACK_RESULT" "$FINAL_RESULT" "true" "$PRIMARY_PROVIDER" "$PRIMARY_REASON"
update_manifest
python3 -m json.tool "$FINAL_RESULT"

if [[ "$FALLBACK_STATUS" -eq 0 ]]; then
  exit 0
fi

exit "$FALLBACK_STATUS"
