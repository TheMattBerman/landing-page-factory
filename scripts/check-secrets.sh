#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

TRACKED_FILE="$TMP_DIR/tracked.txt"
STAGED_FILE="$TMP_DIR/staged.txt"

git -C "$ROOT_DIR" ls-files -z | xargs -0 cat -- 2>/dev/null >"$TRACKED_FILE" || true
git -C "$ROOT_DIR" diff --cached --binary >"$STAGED_FILE" || true

has_match() {
  local pattern="$1"
  if rg -n --no-messages --pcre2 "$pattern" "$TRACKED_FILE" "$STAGED_FILE" >/dev/null; then
    return 0
  fi
  return 1
}

FAILURES=()

if has_match 'bloom_sk_[A-Za-z0-9]+'; then
  FAILURES+=("Bloom secret token pattern detected in tracked or staged content")
fi

if has_match '(?m)^[[:space:]]*(?!#)(BLOOM_API_KEY|FIRECRAWL_API_KEY|OPENAI_API_KEY|ANTHROPIC_API_KEY|GOOGLE_API_KEY|FAL_KEY)\s*=\s*(?!your_key_here\b|xxx\b|changeme\b|example\b)[^#[:space:]]{12,}'; then
  FAILURES+=("Real-looking API key assignment detected in tracked or staged content")
fi

if [[ ${#FAILURES[@]} -gt 0 ]]; then
  printf 'Secret guard failed:\n' >&2
  for failure in "${FAILURES[@]}"; do
    printf '  - %s\n' "$failure" >&2
  done
  exit 1
fi

printf 'Secret guard passed.\n'
