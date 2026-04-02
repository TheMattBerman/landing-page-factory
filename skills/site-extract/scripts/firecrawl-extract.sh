#!/usr/bin/env bash
# firecrawl-extract.sh — Extract brand DNA via Firecrawl API v2
# Usage: bash firecrawl-extract.sh --url "https://example.com" [--output workspace/brand]
#
# Uses Firecrawl's branding format for structured brand identity extraction
# (logo, colors, fonts, spacing, UI components) plus markdown for content.
#
# Requires: FIRECRAWL_API_KEY env var (get one at https://firecrawl.dev)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
URL=""
OUTPUT_DIR="workspace/brand"

while [[ $# -gt 0 ]]; do
  case $1 in
    --url) URL="$2"; shift 2 ;;
    --output) OUTPUT_DIR="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

if [[ -z "$URL" ]]; then
  echo "Error: --url is required"
  echo "Usage: bash firecrawl-extract.sh --url 'https://example.com'"
  exit 1
fi

# Load API key from env or credentials file
if [[ -z "${FIRECRAWL_API_KEY:-}" ]]; then
  PROJECT_ROOT=""
  if [[ -n "${LPF_ROOT:-}" && -f "${LPF_ROOT}/.env" ]]; then
    PROJECT_ROOT="$LPF_ROOT"
  else
    CANDIDATE="$SCRIPT_DIR"
    while [[ "$CANDIDATE" != "/" ]]; do
      if [[ -f "$CANDIDATE/.env" && -f "$CANDIDATE/AGENTS.md" ]]; then
        PROJECT_ROOT="$CANDIDATE"
        break
      fi
      CANDIDATE="$(dirname "$CANDIDATE")"
    done
  fi

  if [[ -n "$PROJECT_ROOT" && -f "$PROJECT_ROOT/.env" ]]; then
    # Export local .env values so shell invocation works without requiring set -a.
    set -a
    # shellcheck disable=SC1090
    source "$PROJECT_ROOT/.env"
    set +a
  fi
fi

if [[ -z "${FIRECRAWL_API_KEY:-}" ]]; then
  if [[ -f ~/.openclaw/credentials/firecrawl.env ]]; then
    source ~/.openclaw/credentials/firecrawl.env
  fi
fi

if [[ -z "${FIRECRAWL_API_KEY:-}" ]]; then
  echo "Error: FIRECRAWL_API_KEY not set"
  echo "Get a free key at https://firecrawl.dev and set it:"
  echo "  export FIRECRAWL_API_KEY=fc-your-key-here"
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

echo "🔥 Extracting brand DNA via Firecrawl v2: $URL"

# Use Firecrawl v2 with branding + markdown + screenshot formats
# branding = structured brand identity (logo, colors, fonts, spacing, UI)
# markdown = page content for claim/proof extraction
# screenshot = visual reference
PAYLOAD=$(cat <<EOF
{
  "url": "$URL",
  "formats": ["branding", "markdown", "screenshot"],
  "onlyMainContent": false,
  "maxAge": 172800000
}
EOF
)

echo "  → Calling Firecrawl v2 API..."
RESPONSE=$(curl -s -X POST "https://api.firecrawl.dev/v2/scrape" \
  -H "Authorization: Bearer $FIRECRAWL_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  --max-time 60)

# Check for errors
if echo "$RESPONSE" | jq -e '.success == false' &>/dev/null; then
  ERROR=$(echo "$RESPONSE" | jq -r '.error // "Unknown error"')
  echo "❌ Firecrawl error: $ERROR"
  echo "$RESPONSE" | jq '.' > "$OUTPUT_DIR/firecrawl-error.json" 2>/dev/null
  exit 1
fi

# Save raw response
echo "$RESPONSE" | jq '.' > "$OUTPUT_DIR/firecrawl-raw.json" 2>/dev/null || echo "$RESPONSE" > "$OUTPUT_DIR/firecrawl-raw.json"

# Extract branding and metadata
BRANDING=$(echo "$RESPONSE" | jq '.data.branding // {}' 2>/dev/null)
METADATA=$(echo "$RESPONSE" | jq '.data.metadata // {}' 2>/dev/null)
echo "$BRANDING" | jq '.' > "$OUTPUT_DIR/branding.json" 2>/dev/null

echo "$METADATA" | jq '.' > "$OUTPUT_DIR/extract-metadata.json" 2>/dev/null

# Extract markdown content for claim/proof analysis
MARKDOWN=$(echo "$RESPONSE" | jq -r '.data.markdown // empty' 2>/dev/null)
printf '%s
' "$MARKDOWN" > "$OUTPUT_DIR/extract-markdown.md"
printf '%s
' "$MARKDOWN" > "$OUTPUT_DIR/extract.md"

# Brand name fallback order: branding.brand_name -> branding.images.logoAlt -> metadata title fields -> hostname
HOSTNAME=$(printf '%s' "$URL" | sed -E 's|https?://||; s|/.*$||; s|^www\.||')
TITLE=$(echo "$METADATA" | jq -r '.title // .ogTitle // .["og:title"] // empty' 2>/dev/null)
LOGO_ALT=$(echo "$BRANDING" | jq -r '.images.logoAlt // empty' 2>/dev/null)
BRAND_NAME=$(echo "$BRANDING" | jq -r '.brand_name // .brand // empty' 2>/dev/null)
if [[ -z "$BRAND_NAME" || "$BRAND_NAME" == "null" ]]; then BRAND_NAME="$LOGO_ALT"; fi
if [[ -z "$BRAND_NAME" || "$BRAND_NAME" == "null" ]]; then BRAND_NAME="$TITLE"; fi
if [[ -n "$BRAND_NAME" && "$BRAND_NAME" != "null" ]]; then
  BRAND_NAME=$(printf '%s' "$BRAND_NAME" | sed -E 's/[[:space:]]+[—–|-].*$//' | sed -E 's/[[:space:]]*\|.*$//' | sed -E 's/^[[:space:]]+|[[:space:]]+$//g')
fi
if [[ -z "$BRAND_NAME" || "$BRAND_NAME" == "null" ]]; then
  BRAND_NAME=$(printf '%s' "$HOSTNAME" | awk -F'.' '{print $1}')
fi

# Build canonical extract.json matching downstream expectations
jq -n   --arg brand "$BRAND_NAME"   --arg source "$URL"   --arg hostname "$HOSTNAME"   --arg title "$TITLE"   --arg description "$(echo "$METADATA" | jq -r '.description // .ogDescription // .["og:description"] // empty' 2>/dev/null)"   --arg logo "$(echo "$BRANDING" | jq -r '.logo // .images.logo // empty' 2>/dev/null)"   --arg screenshot "$(echo "$RESPONSE" | jq -r '.data.screenshot // empty' 2>/dev/null)"   --arg confidence "medium"   --argjson branding "$BRANDING"   --argjson metadata "$METADATA"   '{
    brand: $brand,
    category: ($metadata.description // ""),
    offer: ($metadata.description // ""),
    source: $source,
    hostname: $hostname,
    hero_language: {headline: $title, subheadline: ($metadata.description // "")},
    claims: [],
    proof_inventory: [],
    cta_inventory: [],
    mechanism_language: [],
    trust_cues: [],
    page_patterns: [],
    visual_motifs: [],
    audience_signals: [],
    missing_flags: [],
    logo_url: $logo,
    screenshot_url: $screenshot,
    branding: $branding,
    metadata: $metadata,
    confidence: $confidence
  }' > "$OUTPUT_DIR/extract.json"

# Extract screenshot URL if available
SCREENSHOT_URL=$(echo "$RESPONSE" | jq -r '.data.screenshot // empty' 2>/dev/null)
if [[ -n "$SCREENSHOT_URL" ]]; then
  echo "  → Downloading screenshot..."
  curl -sL "$SCREENSHOT_URL" -o "$OUTPUT_DIR/screenshot.png" --max-time 15 2>/dev/null || echo "  ⚠ Screenshot download failed (URL may have expired)"
fi

# Build palette.json from branding data
COLORS=$(echo "$BRANDING" | jq '.colors // {}' 2>/dev/null)
FONTS=$(echo "$BRANDING" | jq '.fonts // []' 2>/dev/null)
LOGO=$(echo "$BRANDING" | jq -r '.logo // empty' 2>/dev/null)
COLOR_SCHEME=$(echo "$BRANDING" | jq -r '.colorScheme // "unknown"' 2>/dev/null)
SPACING=$(echo "$BRANDING" | jq '.spacing // {}' 2>/dev/null)

cat > "$OUTPUT_DIR/palette.json" << EOF
{
  "source": "$URL",
  "colorScheme": "$COLOR_SCHEME",
  "logo": "$LOGO",
  "colors": $COLORS,
  "fonts": $FONTS,
  "spacing": $SPACING,
  "extracted_at": "$(date -Iseconds)",
  "method": "firecrawl-v2-branding"
}
EOF

# Download logo if URL found from branding format
if [[ -n "$LOGO" && "$LOGO" != "null" ]]; then
  echo "  → Downloading logo..."
  LOGO_EXT="${LOGO##*.}"
  [[ "$LOGO_EXT" =~ ^(png|jpg|jpeg|svg|webp|ico)$ ]] || LOGO_EXT="png"
  curl -sL "$LOGO" -o "$OUTPUT_DIR/logo.$LOGO_EXT" --max-time 10 2>/dev/null || echo "  ⚠ Logo download failed"
else
  # Fallback: try to find logo in markdown content or metadata
  MARKDOWN_FILE="$OUTPUT_DIR/extract-markdown.md"
  if [[ -f "$MARKDOWN_FILE" ]]; then
    LOGO_FALLBACK=$(python3 - "$MARKDOWN_FILE" <<'PY'
import re
import sys
from pathlib import Path

text = Path(sys.argv[1]).read_text(encoding="utf-8")
match = re.search(r'https?://[^\s\)"]+logo[^\s\)"]*\.(?:png|jpg|jpeg|svg|webp)', text, re.I)
print(match.group(0) if match else "")
PY
)
    if [[ -n "$LOGO_FALLBACK" ]]; then
      echo "  → Logo not in branding data, found in page content: $LOGO_FALLBACK"
      LOGO="$LOGO_FALLBACK"
      LOGO_EXT="${LOGO##*.}"
      curl -sL "$LOGO" -o "$OUTPUT_DIR/logo.$LOGO_EXT" --max-time 10 2>/dev/null || echo "  ⚠ Logo download failed"
      # Update palette.json with found logo
      TMP_PALETTE=$(mktemp)
      jq --arg logo "$LOGO" '.logo = $logo' "$OUTPUT_DIR/palette.json" > "$TMP_PALETTE" && mv "$TMP_PALETTE" "$OUTPUT_DIR/palette.json"
    else
      echo "  ⚠ No logo found in branding data or page content"
    fi
  fi
fi

echo ""
echo "✅ Brand extraction complete!"
echo "   Output: $OUTPUT_DIR/"
echo "   Files:"
ls -1 "$OUTPUT_DIR"/ 2>/dev/null | sed 's/^/     /'
echo ""

# Show key brand data
echo "   Brand: $BRAND_NAME"
echo "   Brand identity:"
echo "     Color scheme: $COLOR_SCHEME"
echo "     Logo: ${LOGO:-not found}"
echo "     Primary color: $(echo "$COLORS" | jq -r '.primary // "n/a"' 2>/dev/null)"
echo "     Font: $(echo "$FONTS" | jq -r '.[0].family // "n/a"' 2>/dev/null)"
echo ""
echo "→ Next: Run /brand-profile to build full identity"
echo "→ Or: Run /page-strategy to plan the page"
