while true; do
	python -m unittest discover
	date
	inotifywait -e modify -r  . --exclude '(.pyc|.swp|.png)'
done
