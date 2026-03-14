while true; do
	python3 -m mypy
	python3 -m unittest discover
	date
	inotifywait -q -e modify -r  . --exclude '(.pyc|.swp|.png)'
done
