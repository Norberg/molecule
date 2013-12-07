while true; do
	python3 -m unittest discover
	date
	inotifywait -e modify -r  . --exclude '(.pyc|.swp|.png)'
done
