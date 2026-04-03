#!/usr/bin/env sh

set -eu

UV_BIN="${UV_BIN:-$HOME/.local/bin/uv}"
UV_CACHE_DIR="${UV_CACHE_DIR:-/tmp/uv-cache}"
PYGLET_HEADLESS="${PYGLET_HEADLESS:-1}"

run_once() {
	mkdir -p "$UV_CACHE_DIR"
	UV_CACHE_DIR="$UV_CACHE_DIR" "$UV_BIN" run mypy
	UV_CACHE_DIR="$UV_CACHE_DIR" PYGLET_HEADLESS="$PYGLET_HEADLESS" "$UV_BIN" run python -m unittest discover
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
