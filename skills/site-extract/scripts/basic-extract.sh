#!/usr/bin/env bash
# site-extract.sh — Scrape a URL and extract brand DNA
# Usage: bash site-extract.sh --url "https://example.com" [--deep] [--product "https://example.com/product"]

set -euo pipefail

URL=""
DEEP=false
PRODUCT_URL=""
OUTPUT_DIR="workspace/brand"

while [[ $# -gt 0 ]]; do
  case $1 in
    --url) URL="$2"; shift 2 ;;
    --deep) DEEP=true; shift ;;
    --product) PRODUCT_URL="$2"; shift 2 ;;
    --output) OUTPUT_DIR="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

if [[ -z "$URL" ]]; then
  echo "Error: --url is required"
  echo "Usage: bash site-extract.sh --url 'https://example.com' [--deep] [--product 'url']"
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

echo "🔍 Extracting brand DNA from: $URL"

# Fetch the page HTML
echo "  → Fetching page..."
PAGE_HTML=$(curl -sL -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
  --max-time 30 \
  "$URL" 2>/dev/null || echo "FETCH_FAILED")

if [[ "$PAGE_HTML" == "FETCH_FAILED" || -z "$PAGE_HTML" ]]; then
  echo "❌ Failed to fetch $URL"
  exit 1
fi

# Extract colors from CSS
echo "  → Extracting colors..."
COLORS=$(echo "$PAGE_HTML" | grep -oP '(#[0-9a-fA-F]{3,8}|rgb\([^)]+\)|rgba\([^)]+\))' | sort | uniq -c | sort -rn | head -20)

# Extract font families
echo "  → Extracting fonts..."
FONTS=$(echo "$PAGE_HTML" | grep -oP "font-family:\s*['\"]?([^;\"'}\)]+)" | sed 's/font-family:\s*//' | sort | uniq -c | sort -rn | head -10)

# Extract Google Fonts
GFONTS=$(echo "$PAGE_HTML" | grep -oP 'fonts\.googleapis\.com/css2?\?family=[^"'"'"' >]+' | head -5)

# Extract meta theme-color
THEME_COLOR=$(echo "$PAGE_HTML" | grep -oP '<meta[^>]*name="theme-color"[^>]*content="([^"]+)"' | grep -oP 'content="[^"]+' | sed 's/content="//')

# Extract title
TITLE=$(echo "$PAGE_HTML" | grep -oP '<title[^>]*>([^<]+)</title>' | sed 's/<[^>]*>//g' | head -1)

# Extract meta description
META_DESC=$(echo "$PAGE_HTML" | grep -oP '<meta[^>]*name="description"[^>]*content="([^"]+)"' | grep -oP 'content="[^"]+' | sed 's/content="//' | head -1)

# Extract OG data
OG_TITLE=$(echo "$PAGE_HTML" | grep -oP '<meta[^>]*property="og:title"[^>]*content="([^"]+)"' | grep -oP 'content="[^"]+' | sed 's/content="//' | head -1)
OG_DESC=$(echo "$PAGE_HTML" | grep -oP '<meta[^>]*property="og:description"[^>]*content="([^"]+)"' | grep -oP 'content="[^"]+' | sed 's/content="//' | head -1)
OG_IMAGE=$(echo "$PAGE_HTML" | grep -oP '<meta[^>]*property="og:image"[^>]*content="([^"]+)"' | grep -oP 'content="[^"]+' | sed 's/content="//' | head -1)

# Extract visible text (strip tags, compress whitespace)
echo "  → Extracting text content..."
VISIBLE_TEXT=$(echo "$PAGE_HTML" | sed 's/<script[^>]*>.*<\/script>//g; s/<style[^>]*>.*<\/style>//g' | sed 's/<[^>]*>//g' | tr -s '[:space:]' '\n' | head -500)

# Extract button text (CTA signals)
BUTTONS=$(echo "$PAGE_HTML" | grep -oP '<(button|a)[^>]*class="[^"]*btn[^"]*"[^>]*>([^<]+)<' | sed 's/<[^>]*>//g' | head -10)
BUTTONS2=$(echo "$PAGE_HTML" | grep -oP '<button[^>]*>([^<]+)</button>' | sed 's/<[^>]*>//g' | head -10)

# Extract structured data
JSONLD=$(echo "$PAGE_HTML" | grep -oP '<script type="application/ld\+json">[^<]+</script>' | sed 's/<[^>]*>//g' | head -3)

# Save raw extraction data
cat > "$OUTPUT_DIR/extract-raw.json" << RAWEOF
{
  "url": "$URL",
  "title": $(echo "$TITLE" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))" 2>/dev/null || echo "\"\""),
  "meta_description": $(echo "$META_DESC" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))" 2>/dev/null || echo "\"\""),
  "og_title": $(echo "$OG_TITLE" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))" 2>/dev/null || echo "\"\""),
  "og_description": $(echo "$OG_DESC" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))" 2>/dev/null || echo "\"\""),
  "og_image": $(echo "$OG_IMAGE" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))" 2>/dev/null || echo "\"\""),
  "theme_color": "$THEME_COLOR",
  "extracted_at": "$(date -Iseconds)"
}
RAWEOF

# Save colors
echo "$COLORS" > "$OUTPUT_DIR/extract-colors.txt"

# Save fonts
echo "== Font Families ==" > "$OUTPUT_DIR/extract-fonts.txt"
echo "$FONTS" >> "$OUTPUT_DIR/extract-fonts.txt"
echo "" >> "$OUTPUT_DIR/extract-fonts.txt"
echo "== Google Fonts ==" >> "$OUTPUT_DIR/extract-fonts.txt"
echo "$GFONTS" >> "$OUTPUT_DIR/extract-fonts.txt"

# Save visible text
echo "$VISIBLE_TEXT" > "$OUTPUT_DIR/extract-text.txt"

# Save buttons/CTAs
echo "== Buttons ==" > "$OUTPUT_DIR/extract-ctas.txt"
echo "$BUTTONS" >> "$OUTPUT_DIR/extract-ctas.txt"
echo "$BUTTONS2" >> "$OUTPUT_DIR/extract-ctas.txt"

# Save structured data
echo "$JSONLD" > "$OUTPUT_DIR/extract-jsonld.txt"

# Deep mode: find and scrape additional pages
if [[ "$DEEP" == "true" ]]; then
  echo "  → Deep mode: finding additional pages..."
  
  # Extract internal links
  DOMAIN=$(echo "$URL" | grep -oP 'https?://[^/]+')
  LINKS=$(echo "$PAGE_HTML" | grep -oP "href=\"(/[^\"]+|${DOMAIN}[^\"]+)\"" | sed 's/href="//;s/"//' | sort -u)
  
  # Find about, pricing, product pages
  ABOUT=$(echo "$LINKS" | grep -i 'about' | head -1)
  PRICING=$(echo "$LINKS" | grep -i 'pric' | head -1)
  PRODUCT=$(echo "$LINKS" | grep -iE 'product|shop|collection' | head -1)
  
  for EXTRA_PATH in "$ABOUT" "$PRICING" "$PRODUCT" "$PRODUCT_URL"; do
    if [[ -n "$EXTRA_PATH" ]]; then
      # Make absolute URL if relative
      if [[ "$EXTRA_PATH" == /* ]]; then
        EXTRA_URL="${DOMAIN}${EXTRA_PATH}"
      else
        EXTRA_URL="$EXTRA_PATH"
      fi
      
      echo "  → Scraping: $EXTRA_URL"
      EXTRA_HTML=$(curl -sL -A "Mozilla/5.0" --max-time 20 "$EXTRA_URL" 2>/dev/null || echo "")
      if [[ -n "$EXTRA_HTML" ]]; then
        EXTRA_TEXT=$(echo "$EXTRA_HTML" | sed 's/<script[^>]*>.*<\/script>//g; s/<style[^>]*>.*<\/style>//g' | sed 's/<[^>]*>//g' | tr -s '[:space:]' '\n' | head -300)
        SAFE_NAME=$(echo "$EXTRA_PATH" | sed 's/[^a-zA-Z0-9]/_/g' | head -c 50)
        echo "$EXTRA_TEXT" > "$OUTPUT_DIR/extract-deep-${SAFE_NAME}.txt"
      fi
    fi
  done
fi

echo ""
echo "✅ Brand extraction complete!"
echo "   Output: $OUTPUT_DIR/"
echo "   Files:"
ls -1 "$OUTPUT_DIR"/extract-* 2>/dev/null | sed 's/^/     /'
echo ""
echo "→ Next: Run /brand-profile to build identity from this extract"
echo "→ Or: Run /page-copy to start writing immediately"
