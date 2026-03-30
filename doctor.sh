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
for skill in site-extract page-strategy brand-profile page-copy page-visuals page-build page-qa; do
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

# python3
if command -v python3 &>/dev/null; then
  check "python3 $(python3 --version 2>&1 | awk '{print $2}')" "ok"
else
  check "python3 — not found" "fail"
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

# Pages directory
if [[ -d "workspace/pages" ]]; then
  PAGE_COUNT=$(ls -d workspace/pages/*/ 2>/dev/null | wc -l)
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
