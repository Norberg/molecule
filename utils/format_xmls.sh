FILES=data/molecule/*.cml

for f in $FILES
do
	xmllint --format "$f" --output "$f"
done
