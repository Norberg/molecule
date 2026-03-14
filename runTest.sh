#!/usr/bin/env sh

set -eu

run_once() {
	python3 -m mypy
	python3 -m unittest discover
	date
}

if [ "${1:-}" = "-l" ] || [ "${1:-}" = "--loop" ]; then
	while true; do
		run_once
		inotifywait -q -e modify -r . --exclude '(.pyc|.swp|.png)'
	done
else
	run_once
fi
