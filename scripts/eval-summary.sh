#!/usr/bin/env bash
# eval-summary.sh — Quick variant comparison
# Usage: bash scripts/eval-summary.sh [page-name]
# If no page-name given, summarizes all pages in workspace/pages/
set -euo pipefail

PAGES_DIR="workspace/pages"

if [[ ! -d "$PAGES_DIR" ]]; then
  echo "No workspace/pages/ directory found. Run a page build first."
  exit 1
fi

summarize_page() {
  local page_dir="$1"
  local page_name
  page_name=$(basename "$page_dir")

  local meta="$page_dir/meta.json"
  local qa="$page_dir/qa.md"

  if [[ ! -f "$meta" ]]; then
    echo "$page_name: NO META — build incomplete"
    return
  fi

  if [[ ! -f "$qa" ]]; then
    echo "$page_name: NO QA — run page-qa first"
    return
  fi

  # Try to extract eval block from meta.json
  if command -v jq &>/dev/null; then
    local verdict
    verdict=$(jq -r '.eval.verdict // .verdict // "unknown"' "$meta" 2>/dev/null || echo "unknown")
    local overall
    overall=$(jq -r '.eval.overall // "n/a"' "$meta" 2>/dev/null || echo "n/a")
    local copy
    copy=$(jq -r '.eval.copy_composite // "n/a"' "$meta" 2>/dev/null || echo "n/a")
    local visual
    visual=$(jq -r '.eval.visual_composite // "n/a"' "$meta" 2>/dev/null || echo "n/a")
    local qa_composite
    qa_composite=$(jq -r '.eval.qa_composite // "n/a"' "$meta" 2>/dev/null || echo "n/a")

    local verdict_upper
    verdict_upper=$(echo "$verdict" | tr '[:lower:]' '[:upper:]')

    echo "$page_name: $verdict_upper | copy: $copy | visual: $visual | qa: $qa_composite | overall: $overall"
  else
    # Fallback: just check for verdict in QA
    local verdict_line
    verdict_line=$(grep -i "verdict\|shippable\|draft\|blocked" "$qa" | head -1 || echo "unknown")
    echo "$page_name: $verdict_line"
  fi
}

if [[ $# -ge 1 ]]; then
  # Summarize specific page
  page_dir="$PAGES_DIR/$1"
  if [[ ! -d "$page_dir" ]]; then
    echo "Page '$1' not found in $PAGES_DIR/"
    exit 1
  fi
  summarize_page "$page_dir"
else
  # Summarize all pages
  found=0
  for page_dir in "$PAGES_DIR"/*/; do
    [[ -d "$page_dir" ]] || continue
    summarize_page "$page_dir"
    found=$((found + 1))
  done

  if [[ $found -eq 0 ]]; then
    echo "No pages found in $PAGES_DIR/. Run the pipeline first."
  else
    echo ""
    echo "($found pages)"
  fi
fi
