#!/usr/bin/env bash
set -euo pipefail

ACTION="${1:-}"
JOB_FILE="${2:-}"

if [[ "$ACTION" != "generate" || -z "$JOB_FILE" ]]; then
  echo '{"provider":"nano-banana","status":"failed","reason":"Usage: nano-banana.sh generate JOB_FILE","provider_metadata":{},"notes":[]}'
  exit 1
fi

if [[ ! -f "$JOB_FILE" ]]; then
  echo '{"provider":"nano-banana","status":"failed","reason":"Job file not found","provider_metadata":{},"notes":[]}'
  exit 1
fi

if [[ -z "${NANO_BANANA_COMMAND:-}" ]]; then
  echo '{"provider":"nano-banana","status":"failed","reason":"NANO_BANANA_COMMAND is not configured","provider_metadata":{},"notes":["Set NANO_BANANA_COMMAND to a command that accepts the job JSON path as its final argument and returns a JSON result on stdout."]}'
  exit 10
fi

set +e
OUTPUT="$($NANO_BANANA_COMMAND "$JOB_FILE" 2>&1)"
STATUS=$?
set -e

if [[ "$STATUS" -ne 0 ]]; then
  python3 - <<'PY' "$OUTPUT"
import json
import sys

payload = {
    "provider": "nano-banana",
    "status": "failed",
    "reason": "External Nano Banana command failed",
    "provider_metadata": {},
    "notes": [sys.argv[1]],
}
print(json.dumps(payload))
PY
  exit 10
fi

printf '%s\n' "$OUTPUT"
