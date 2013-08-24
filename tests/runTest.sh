while true; do
	python -m unittest discover
	date
	inotifywait -e modify  ../ --exclude '(.pyc|.swp)'
done
