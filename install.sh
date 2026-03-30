#!/usr/bin/env bash
# Page Factory — Install Script
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION=$(cat "$SCRIPT_DIR/VERSION" 2>/dev/null || echo "0.1.0")

echo "📄 Page Factory v$VERSION — Installing..."
echo ""

# Create workspace directories
mkdir -p workspace/brand
mkdir -p workspace/pages

# Check dependencies
MISSING=()

if ! command -v curl &>/dev/null; then
  MISSING+=("curl")
fi

if ! command -v python3 &>/dev/null; then
  MISSING+=("python3")
fi

if [[ ${#MISSING[@]} -gt 0 ]]; then
  echo "⚠️  Missing dependencies: ${MISSING[*]}"
  echo "   Install them and re-run."
  exit 1
fi

echo "✅ Dependencies OK"
echo "✅ Workspace directories created"
echo ""
echo "Skills installed:"
for skill in "$SCRIPT_DIR"/skills/*/; do
  name=$(basename "$skill")
  echo "  → $name"
done
echo ""
echo "🚀 Ready! Start with:"
echo "   /site-extract https://yoursite.com"
echo ""
echo "Or run the full pipeline:"
echo "   Build me a landing page for https://yoursite.com"
