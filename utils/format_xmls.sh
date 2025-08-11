#!/bin/sh
set -e

# Kataloger med CML-filer att formatera
DIRS="data/molecule data/reactions"

format_file() {
  f="$1"
  [ -e "$f" ] || return 0
  TEMP="$(mktemp)"
  if ! xmllint --format "$f" --output "$TEMP" 2>/dev/null; then
    echo "Skipping (xmllint error): $f" >&2
    rm -f "$TEMP"
    return 0
  fi
  if ! cmp -s "$TEMP" "$f"; then
    mv "$TEMP" "$f"
    echo "Updated: $f"
  else
    rm "$TEMP"
  fi
}

for dir in $DIRS; do
  for f in "$dir"/*.cml; do
    format_file "$f"
  done
done

echo "Formatting complete."