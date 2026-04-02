#!/usr/bin/env bash
# Page Factory — Health Check
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION=$(cat "$SCRIPT_DIR/VERSION" 2>/dev/null || echo "unknown")
PASS=0
FAIL=0
WARN=0

check() {
  local label="$1"
  local result="$2"
  if [[ "$result" == "ok" ]]; then
    echo "  ✅ $label"
    PASS=$((PASS + 1))
  elif [[ "$result" == "warn" ]]; then
    echo "  ⚠️  $label"
    WARN=$((WARN + 1))
  else
    echo "  ❌ $label"
    FAIL=$((FAIL + 1))
  fi
}

echo "🏥 Page Factory v$VERSION — Health Check"
echo ""

# Check skill files exist
echo "Skills:"
for skill in landing-page-factory-orchestrator site-extract page-strategy brand-profile page-copy page-visuals page-build page-qa; do
  if [[ -f "$SCRIPT_DIR/skills/$skill/SKILL.md" ]]; then
    check "$skill" "ok"
  else
    check "$skill — SKILL.md missing" "fail"
  fi
done

echo ""
echo "Dependencies:"

# curl
if command -v curl &>/dev/null; then
  check "curl $(curl --version | head -1 | awk '{print $2}')" "ok"
else
  check "curl — not found" "fail"
fi

if [[ -x "$SCRIPT_DIR/scripts/image-provider.sh" ]]; then
  check "scripts/image-provider.sh present" "ok"
else
  check "scripts/image-provider.sh missing or not executable" "fail"
fi

if [[ -x "$SCRIPT_DIR/scripts/providers/bloom.sh" ]]; then
  check "Bloom provider adapter present" "ok"
else
  check "Bloom provider adapter missing or not executable" "fail"
fi

if [[ -x "$SCRIPT_DIR/scripts/providers/nano-banana.sh" ]]; then
  check "Nano Banana fallback adapter present" "ok"
else
  check "Nano Banana fallback adapter missing or not executable" "fail"
fi

if [[ -x "$SCRIPT_DIR/scripts/check-secrets.sh" ]]; then
  if "$SCRIPT_DIR/scripts/check-secrets.sh" >/dev/null 2>&1; then
    check "secret guard passed" "ok"
  else
    check "secret guard found tracked or staged secrets" "fail"
  fi
else
  check "scripts/check-secrets.sh missing or not executable" "warn"
fi

# python3
if command -v python3 &>/dev/null; then
  check "python3 $(python3 --version 2>&1 | awk '{print $2}')" "ok"
else
  check "python3 — not found" "fail"
fi

if [[ -x "$SCRIPT_DIR/scripts/resolve-visual-assets.py" ]]; then
  check "scripts/resolve-visual-assets.py present" "ok"
else
  check "scripts/resolve-visual-assets.py missing or not executable" "fail"
fi

if [[ -x "$SCRIPT_DIR/scripts/prepare-build-meta.py" ]]; then
  check "scripts/prepare-build-meta.py present" "ok"
else
  check "scripts/prepare-build-meta.py missing or not executable" "fail"
fi

if [[ -x "$SCRIPT_DIR/scripts/select-build-images.py" ]]; then
  check "scripts/select-build-images.py present" "ok"
else
  check "scripts/select-build-images.py missing or not executable" "fail"
fi

if [[ -x "$SCRIPT_DIR/scripts/html-image-context.py" ]]; then
  check "scripts/html-image-context.py present" "ok"
else
  check "scripts/html-image-context.py missing or not executable" "fail"
fi

if [[ -x "$SCRIPT_DIR/scripts/build-page.py" ]]; then
  check "scripts/build-page.py present" "ok"
else
  check "scripts/build-page.py missing or not executable" "fail"
fi

if [[ -x "$SCRIPT_DIR/scripts/page-admin.py" ]]; then
  check "scripts/page-admin.py present" "ok"
else
  check "scripts/page-admin.py missing or not executable" "fail"
fi

if [[ -x "$SCRIPT_DIR/scripts/run-pipeline.py" ]]; then
  check "scripts/run-pipeline.py present" "ok"
else
  check "scripts/run-pipeline.py missing or not executable" "fail"
fi

# jq (optional but helpful)
if command -v jq &>/dev/null; then
  check "jq $(jq --version 2>&1)" "ok"
else
  check "jq — not found (optional, install for better JSON handling)" "warn"
fi

echo ""
echo "Workspace:"

# Brand directory
if [[ -d "workspace/brand" ]]; then
  check "workspace/brand/ exists" "ok"
  # Check for brand files
  if [[ -f "workspace/brand/profile.md" ]]; then
    check "brand profile loaded" "ok"
  else
    check "no brand profile yet (run /site-extract first)" "warn"
  fi
else
  check "workspace/brand/ — run install.sh first" "fail"
fi

if [[ -d "memory" ]]; then
  check "memory/ exists" "ok"
else
  check "memory/ missing (will be created on first orchestrator log)" "warn"
fi

echo ""
echo "Image providers:"

if [[ -n "${BLOOM_API_KEY:-}" ]]; then
  check "BLOOM_API_KEY configured" "ok"
elif [[ -f "$SCRIPT_DIR/.env" ]] && rg -n '^[[:space:]]*BLOOM_API_KEY=' "$SCRIPT_DIR/.env" >/dev/null 2>&1; then
  check "BLOOM_API_KEY configured in local .env" "ok"
else
  check "BLOOM_API_KEY not set (Bloom first-pass generation unavailable)" "warn"
fi

if [[ -n "${NANO_BANANA_COMMAND:-}" ]]; then
  check "NANO_BANANA_COMMAND configured" "ok"
elif [[ -f "$SCRIPT_DIR/.env" ]] && rg -n '^[[:space:]]*NANO_BANANA_COMMAND=' "$SCRIPT_DIR/.env" >/dev/null 2>&1; then
  check "NANO_BANANA_COMMAND configured in local .env" "ok"
else
  check "NANO_BANANA_COMMAND not set (fallback adapter requires external command)" "warn"
fi

# Pages directory
if [[ -d "workspace/pages" ]]; then
  PAGE_COUNT=$(find workspace/pages -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
  check "workspace/pages/ exists ($PAGE_COUNT pages)" "ok"
else
  check "workspace/pages/ — run install.sh first" "fail"
fi

echo ""
echo "────────────────────────"
echo "  ✅ $PASS passed  ⚠️  $WARN warnings  ❌ $FAIL failed"

if [[ $FAIL -gt 0 ]]; then
  echo ""
  echo "Run 'bash install.sh' to fix missing components."
  exit 1
else
  exit 0
fi
