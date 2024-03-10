#!/bin/sh
FILES=data/molecule/*.cml

for f in $FILES
do
  TEMP=$(mktemp) # Create a temporary file for holding formatted content
  xmllint --format "$f" --output "$TEMP" # Format the original file content to the temp file
  # Compare the temporary file with the original to check for changes
  if ! cmp -s "$TEMP" "$f"; then
    mv "$TEMP" "$f" # Replace original file with the temporary file if there are differences
    echo "Updated: $f" # Print information only if the file was reformatted
  else
    rm "$TEMP" # Delete the temporary file if no changes were made
  fi
done