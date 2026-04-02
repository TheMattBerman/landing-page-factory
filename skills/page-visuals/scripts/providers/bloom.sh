#!/usr/bin/env bash
set -euo pipefail

ACTION="${1:-}"
JOB_FILE="${2:-}"

if [[ "$ACTION" != "generate" || -z "$JOB_FILE" ]]; then
  echo '{"provider":"bloom","status":"failed","reason":"Usage: bloom.sh generate JOB_FILE","provider_metadata":{},"notes":[]}'
  exit 1
fi

if [[ ! -f "$JOB_FILE" ]]; then
  echo '{"provider":"bloom","status":"failed","reason":"Job file not found","provider_metadata":{},"notes":[]}'
  exit 1
fi

if [[ -z "${BLOOM_API_KEY:-}" ]]; then
  echo '{"provider":"bloom","status":"failed","reason":"BLOOM_API_KEY is not configured","provider_metadata":{},"notes":["Set BLOOM_API_KEY to use Bloom as the primary image provider."]}'
  exit 10
fi

TMP_DIR="$(mktemp -d)"
cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

read_job() {
  python3 - "$JOB_FILE" "$1" <<'PY'
import json
import sys

path, key = sys.argv[1:3]
with open(path, encoding="utf-8") as fh:
    job = json.load(fh)
value = job
for part in key.split("."):
    value = value.get(part) if isinstance(value, dict) else None
if value is None:
    print("")
elif isinstance(value, (dict, list)):
    print(json.dumps(value))
else:
    print(value)
PY
}

JOB_SOURCE_URL="$(read_job source_url)"
JOB_OUTPUT_PATH="$(read_job output_path)"
JOB_PROMPT="$(read_job prompt)"
JOB_ASPECT_RATIO="$(read_job aspect_ratio)"
JOB_BRAND_NAME="$(read_job brand_name)"
JOB_REFS_JSON="$(read_job refs)"

if [[ -z "${BLOOM_BRAND_ID:-}" && -z "$JOB_SOURCE_URL" ]]; then
  echo '{"provider":"bloom","status":"failed","reason":"Bloom requires source_url or BLOOM_BRAND_ID for onboarding","provider_metadata":{},"notes":["Pass --source-url or set BLOOM_BRAND_ID."]}'
  exit 10
fi

api_call() {
  local method="$1"
  local path="$2"
  local body="${3:-}"
  local response_file="$TMP_DIR/response.json"
  local status

  if [[ -n "$body" ]]; then
    status="$(curl -sS -o "$response_file" -w '%{http_code}' \
      -X "$method" "https://www.trybloom.ai/api/v1$path" \
      -H "Authorization: Bearer $BLOOM_API_KEY" \
      -H "Content-Type: application/json" \
      --data "$body")"
  else
    status="$(curl -sS -o "$response_file" -w '%{http_code}' \
      -X "$method" "https://www.trybloom.ai/api/v1$path" \
      -H "Authorization: Bearer $BLOOM_API_KEY")"
  fi

  if [[ "$status" -lt 200 || "$status" -ge 300 ]]; then
    python3 - "$response_file" "$status" <<'PY'
import json
import sys

path, status = sys.argv[1], sys.argv[2]
try:
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
except Exception:
    data = {}
message = data.get("error", {}).get("message") or data.get("message") or f"Bloom API request failed with HTTP {status}"
payload = {
    "provider": "bloom",
    "status": "failed",
    "reason": message,
    "provider_metadata": {"http_status": int(status)},
    "notes": [],
}
print(json.dumps(payload))
PY
    return 10
  fi

  cat "$response_file"
}

normalize_url() {
  python3 - "$1" <<'PY'
import sys
from urllib.parse import urlparse

raw = sys.argv[1].strip()
if not raw:
    print("")
    raise SystemExit
parsed = urlparse(raw)
scheme = parsed.scheme.lower() or "https"
netloc = parsed.netloc.lower()
if netloc.startswith("www."):
    netloc = netloc[4:]
path = parsed.path.rstrip("/")
print(f"{scheme}://{netloc}{path}")
PY
}

find_brand_id() {
  local source_url="$1"
  local normalized_source="$(normalize_url "$source_url")"
  local brands_json

  if ! brands_json="$(api_call GET '/brands?limit=100')" ; then
    return 10
  fi

  python3 - "$normalized_source" "$brands_json" <<'PY'
import json
import sys
from urllib.parse import urlparse

source = sys.argv[1]
data = json.loads(sys.argv[2])
brands = data.get("data", {}).get("brands", [])

def normalize(raw):
    if not raw:
        return ""
    parsed = urlparse(raw)
    netloc = parsed.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    return f"{(parsed.scheme or 'https').lower()}://{netloc}{parsed.path.rstrip('/')}"

matches = []
for brand in brands:
    if normalize(brand.get("url")) == source:
        matches.append(brand)
for brand in matches:
    if brand.get("status") == "ready":
        print(brand.get("id", ""))
        raise SystemExit
if matches:
    print(matches[0].get("id", ""))
    raise SystemExit
print("")
PY
}

wait_for_brand() {
  local brand_id="$1"
  api_call GET "/brands/$brand_id?wait=true&timeout=120"
}

create_brand() {
  local body
  body="$(python3 - "$JOB_SOURCE_URL" <<'PY'
import json
import sys

source_url = sys.argv[1]
print(json.dumps({"url": source_url}))
PY
)"
  api_call POST "/brands" "$body"
}

upload_refs() {
  python3 - "$JOB_REFS_JSON" <<'PY'
import json
import sys

refs = json.loads(sys.argv[1] or "[]")
for ref in refs:
    print(ref)
PY
}

BRAND_ID="${BLOOM_BRAND_ID:-}"
NOTES=()

if [[ -z "$BRAND_ID" ]]; then
  BRAND_ID="$(find_brand_id "$JOB_SOURCE_URL" || true)"
fi

if [[ -z "$BRAND_ID" ]]; then
  create_output="$(create_brand)" || {
    echo "$create_output"
    exit 10
  }
  BRAND_ID="$(python3 - "$create_output" <<'PY'
import json
import sys

data = json.loads(sys.argv[1])
print(data.get("data", {}).get("id", ""))
PY
)"
  NOTES+=("Created Bloom brand from source URL.")
fi

brand_output="$(wait_for_brand "$BRAND_ID")" || {
  echo "$brand_output"
  exit 10
}

BRAND_STATUS="$(python3 - "$brand_output" <<'PY'
import json
import sys

data = json.loads(sys.argv[1])
print(data.get("data", {}).get("status", ""))
PY
)"

if [[ "$BRAND_STATUS" != "ready" ]]; then
  python3 - "$brand_output" "$JOB_BRAND_NAME" <<'PY'
import json
import sys

brand_output = json.loads(sys.argv[1])
brand_name = sys.argv[2]
status = brand_output.get("data", {}).get("status", "unknown")
payload = {
    "provider": "bloom",
    "status": "failed",
    "reason": f"Bloom brand is not ready (status: {status})",
    "brand_context_source": "repo_profile+bloom_onboarding",
    "provider_metadata": {
        "brand_id": brand_output.get("data", {}).get("id"),
        "brand_status": status,
        "brand_name": brand_output.get("data", {}).get("name") or brand_name or None,
    },
    "notes": ["Fill missing Bloom brand context from repo brand artifacts, then retry."],
}
print(json.dumps(payload))
PY
  exit 10
fi

REFERENCE_IDS=()
LOCAL_REF_WARNINGS=()
while IFS= read -r ref; do
  [[ -z "$ref" ]] && continue
  if [[ "$ref" =~ ^https?:// ]]; then
    ref_body="$(python3 - "$ref" "$BRAND_ID" <<'PY'
import json
import sys

print(json.dumps({"imageUrl": sys.argv[1], "brandSessionId": sys.argv[2]}))
PY
)"
    ref_output="$(api_call POST "/images/uploads" "$ref_body")" || {
      echo "$ref_output"
      exit 10
    }
    ref_id="$(python3 - "$ref_output" <<'PY'
import json
import sys

data = json.loads(sys.argv[1])
print(data.get("data", {}).get("id", ""))
PY
)"
    if [[ -n "$ref_id" ]]; then
      REFERENCE_IDS+=("$ref_id")
    fi
  else
    LOCAL_REF_WARNINGS+=("Local ref could not be uploaded to Bloom without a public URL: $ref")
  fi
done < <(upload_refs)

payload_file="$TMP_DIR/generate.json"
python3 - "$JOB_PROMPT" "$BRAND_ID" "$JOB_ASPECT_RATIO" "$payload_file" "${REFERENCE_IDS[@]-}" <<'PY'
import json
import sys

prompt = sys.argv[1]
brand_id = sys.argv[2]
aspect_ratio = sys.argv[3]
payload_file = sys.argv[4]
reference_ids = [value for value in sys.argv[5:] if value]

payload = {
    "prompt": prompt,
    "brandSessionId": brand_id,
    "aspectRatio": aspect_ratio,
    "imageSize": "2K",
    "model": "standard",
    "variantCount": 1,
}
if reference_ids:
    payload["referenceImageIds"] = reference_ids

with open(payload_file, "w", encoding="utf-8") as fh:
    json.dump(payload, fh)
PY

generation_output="$(api_call POST "/images/generations" "$(cat "$payload_file")")" || {
  echo "$generation_output"
  exit 10
}

IMAGE_ID="$(python3 - "$generation_output" <<'PY'
import json
import sys

data = json.loads(sys.argv[1])
ids = data.get("data", {}).get("ids", [])
print(ids[0] if ids else "")
PY
)"

if [[ -z "$IMAGE_ID" ]]; then
  echo '{"provider":"bloom","status":"failed","reason":"Bloom did not return an image ID","provider_metadata":{},"notes":[]}'
  exit 10
fi

image_output="$(api_call GET "/images/$IMAGE_ID?wait=true&timeout=120")" || {
  echo "$image_output"
  exit 10
}

IMAGE_STATUS="$(python3 - "$image_output" <<'PY'
import json
import sys

data = json.loads(sys.argv[1])
print(data.get("data", {}).get("status", ""))
PY
)"

if [[ "$IMAGE_STATUS" != "completed" ]]; then
  python3 - <<'PY' "$image_output" "$BRAND_ID"
import json
import sys

image_output = json.loads(sys.argv[1])
brand_id = sys.argv[2]
payload = {
    "provider": "bloom",
    "status": "failed",
    "reason": f"Bloom image generation did not complete (status: {image_output.get('data', {}).get('status', 'unknown')})",
    "brand_context_source": "repo_profile+bloom_onboarding",
    "provider_metadata": {
        "brand_id": brand_id,
        "image_id": image_output.get("data", {}).get("id"),
        "image_status": image_output.get("data", {}).get("status"),
    },
    "notes": [],
}
print(json.dumps(payload))
PY
  exit 10
fi

IMAGE_URL="$(python3 - "$image_output" <<'PY'
import json
import sys

data = json.loads(sys.argv[1])
print(data.get("data", {}).get("imageUrl", ""))
PY
)"

mkdir -p "$(dirname "$JOB_OUTPUT_PATH")"
curl -sSL "$IMAGE_URL" -o "$JOB_OUTPUT_PATH"

REFERENCE_IDS_JSON="$(python3 - "${REFERENCE_IDS[@]-}" <<'PY'
import json
import sys

print(json.dumps([value for value in sys.argv[1:] if value]))
PY
)"

python3 - "$brand_output" "$image_output" "$JOB_OUTPUT_PATH" "$REFERENCE_IDS_JSON" "${NOTES[*]-}" "${LOCAL_REF_WARNINGS[*]-}" <<'PY'
import json
import sys

brand = json.loads(sys.argv[1]).get("data", {})
image = json.loads(sys.argv[2]).get("data", {})
local_path = sys.argv[3]
reference_image_ids = json.loads(sys.argv[4])
notes = [value for value in sys.argv[5:] if value]

payload = {
    "provider": "bloom",
    "status": "completed",
    "reason": None,
    "local_path": local_path,
    "brand_context_source": "repo_profile+bloom_onboarding",
    "provider_metadata": {
        "brand_id": brand.get("id"),
        "brand_status": brand.get("status"),
        "brand_name": brand.get("name"),
        "brand_url": brand.get("url"),
        "image_id": image.get("id"),
        "variant_group_id": image.get("variantGroupId"),
        "remote_image_url": image.get("imageUrl"),
        "reference_image_ids": reference_image_ids,
        "action_type": image.get("actionType"),
        "width": image.get("width"),
        "height": image.get("height"),
    },
    "notes": notes,
}
print(json.dumps(payload))
PY
