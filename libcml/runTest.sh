while true; do
	python Test.py
	inotifywait -e modify  *.py
done
