while true; do
	python Test.py
	date
	inotifywait -e modify  *.py
done
