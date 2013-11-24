while true; do
	echo "===== Python 2.x ====="
	python -m unittest discover
	echo "===== Python 3.x ====="
	python3 -m unittest discover
	date
	inotifywait -e modify -r  . --exclude '(.pyc|.swp|.png)'
done
