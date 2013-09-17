while true; do
	python -m unittest discover
	python3 -m unittest discover
	date
	inotifywait -e modify -r  . --exclude '(.pyc|.swp|.png)'
done
