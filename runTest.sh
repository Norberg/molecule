MYPATH=`pwd -P`
while true; do
	export PYTHONPATH=${PYTHONPATH}:${MYPATH}
	python -m unittest discover
	date
	inotifywait -e modify -r  . --exclude '(.pyc|.swp|.png)'
done
