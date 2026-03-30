#!/usr/bin/env bash
# firecrawl-extract.sh — Extract brand DNA via Firecrawl API
# Usage: bash firecrawl-extract.sh --url "https://example.com" [--output workspace/brand]
#
# Requires: FIRECRAWL_API_KEY env var (get one at https://firecrawl.dev)

set -euo pipefail

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

echo "🔥 Extracting brand DNA via Firecrawl: $URL"

# Build the extraction schema
SCHEMA='{
  "url": "'"$URL"'",
  "formats": ["markdown", "extract"],
  "extract": {
    "schema": {
      "type": "object",
      "properties": {
        "brand_name": {"type": "string", "description": "Company or brand name"},
        "tagline": {"type": "string", "description": "Brand tagline or slogan"},
        "headline": {"type": "string", "description": "Main hero headline on the page"},
        "subheadline": {"type": "string", "description": "Subheadline or supporting text"},
        "cta_buttons": {"type": "array", "items": {"type": "string"}, "description": "All CTA button text on the page"},
        "value_propositions": {"type": "array", "items": {"type": "string"}, "description": "Key value propositions or benefits"},
        "social_proof": {"type": "array", "items": {"type": "string"}, "description": "Testimonials, customer counts, press mentions, trust badges"},
        "products": {"type": "array", "items": {"type": "object", "properties": {"name": {"type": "string"}, "price": {"type": "string"}, "description": {"type": "string"}}}, "description": "Products or services offered"},
        "colors": {"type": "object", "properties": {"primary": {"type": "string"}, "secondary": {"type": "string"}, "accent": {"type": "string"}, "background": {"type": "string"}, "text": {"type": "string"}}, "description": "Brand colors as hex codes"},
        "fonts": {"type": "object", "properties": {"headline": {"type": "string"}, "body": {"type": "string"}}, "description": "Font families used"},
        "tone": {"type": "string", "description": "Overall tone: casual, professional, playful, luxury, urgent, etc."},
        "target_audience": {"type": "string", "description": "Who this brand is targeting based on language and imagery"},
        "unique_selling_point": {"type": "string", "description": "What makes this brand different from competitors"},
        "objection_handling": {"type": "array", "items": {"type": "string"}, "description": "FAQ items, guarantees, risk reversal language"},
        "logo_url": {"type": "string", "description": "URL of the brand logo if found"}
      }
    }
  }
}'

# Make the API call
echo "  → Calling Firecrawl API..."
RESPONSE=$(curl -s -X POST "https://api.firecrawl.dev/v1/scrape" \
  -H "Authorization: Bearer $FIRECRAWL_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$SCHEMA" \
  --max-time 60)

# Check for errors
if echo "$RESPONSE" | jq -e '.success == false' &>/dev/null; then
  ERROR=$(echo "$RESPONSE" | jq -r '.error // "Unknown error"')
  echo "❌ Firecrawl error: $ERROR"
  exit 1
fi

# Save raw response
echo "$RESPONSE" | jq '.' > "$OUTPUT_DIR/firecrawl-raw.json" 2>/dev/null || echo "$RESPONSE" > "$OUTPUT_DIR/firecrawl-raw.json"

# Extract structured data
echo "$RESPONSE" | jq '.data.extract' > "$OUTPUT_DIR/extract.json" 2>/dev/null

# Extract markdown content
echo "$RESPONSE" | jq -r '.data.markdown // empty' > "$OUTPUT_DIR/extract-markdown.md" 2>/dev/null

# Extract metadata
echo "$RESPONSE" | jq '.data.metadata' > "$OUTPUT_DIR/extract-metadata.json" 2>/dev/null

# Build palette.json from extracted colors
COLORS=$(echo "$RESPONSE" | jq '.data.extract.colors // {}' 2>/dev/null)
FONTS=$(echo "$RESPONSE" | jq '.data.extract.fonts // {}' 2>/dev/null)
BRAND=$(echo "$RESPONSE" | jq -r '.data.extract.brand_name // "Unknown"' 2>/dev/null)

cat > "$OUTPUT_DIR/palette.json" << EOF
{
  "brand": "$BRAND",
  "colors": $COLORS,
  "fonts": $FONTS,
  "source": "$URL",
  "extracted_at": "$(date -Iseconds)"
}
EOF

# Credits used
CREDITS=$(echo "$RESPONSE" | jq '.data.metadata.creditsUsed // "unknown"' 2>/dev/null)

echo ""
echo "✅ Brand extraction complete!"
echo "   Credits used: $CREDITS"
echo "   Output: $OUTPUT_DIR/"
echo "   Files:"
ls -1 "$OUTPUT_DIR"/ 2>/dev/null | sed 's/^/     /'
echo ""
echo "→ Next: Run /brand-profile to build full identity"
echo "→ Or: Jump to /page-copy if extract looks good"
