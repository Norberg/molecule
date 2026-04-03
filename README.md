molecule
========

[![Build Status](https://travis-ci.org/Norberg/molecule.svg?branch=master)](https://travis-ci.org/Norberg/molecule)

Molecule - a chemical reaction puzzle game

Dependencies
-------
We manage Python dependencies with `uv` in `pyproject.toml`.

Python: 3.12 recommended (3.11 should also work, lower versions untested recently).

Core runtime dependencies:
* pyglet==2.1.12 (rendering)
* pymunk==7.1.0 (physics)
* fastapi, uvicorn (local API server)
* numpy (numeric helpers / chemistry utilities)
* Pillow (image handling)
* pycairo (SVG / Cairo based rendering pieces)
* xmlschema (validating CML files)

Editor & chemistry extras:
* PyGObject (GTK3 bindings for the CML editor)
* rdkit (molecule and reaction generation/rendering)
* openbabel-wheel, requests, beautifulsoup4

System packages (Debian/Ubuntu example):
```
sudo apt update && sudo apt install -y \
    build-essential libffi-dev libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev curl llvm libncursesw5-dev xz-utils \
    tk-dev libxml2-dev libxmlsec1-dev liblzma-dev \
    libgirepository1.0-dev libcairo2-dev gir1.2-gtk-3.0 \
    openbabel libsqlite3-dev
```
openbabel is only required for some optional molecule generation workflows.

Install `uv`:
```bash
python3 -m pip install --user uv
```

Create the environment and install dependencies:
```bash
uv python install 3.12
uv sync --group dev
uv sync --group dev --extra cmleditor   # if you want the editor & chemistry features
```

The project uses a 14-day dependency cooldown via `tool.uv.exclude-newer`, so newly published package versions are ignored until they are at least 14 days old.

Run commands through `uv`:
```bash
uv run start.py --help
uv run python -m unittest discover
uv run mypy
```


How to play:
---------
    uv run start.py --help
    Molecule - a chemical reaction puzzle game
    -h --help print this help
    --level=LEVEL choose what level to start on
    -d --debug print debug messages
    --fullscreen play in fullscreen mode
    --width size of window, default=1650
    --height size of window, defaults=1080
    During gameplay:
    ESC - close game
    r - reset current level
    d - switch Graphic debug on/off
    s - skip level
    h - print help for level

Structure:
-------
### libcml/
Library responsible for parsing cml files containing molecules and reactions.

### libreact/
Library responsible for simulating reactions.

### cmleditor/
GUI for editing cml files

### molecule/
Game code.

### data/
All data for the game.

### tests/
All testcases for the game.

### img/
All images.





#### Adding a new atom
Copy one of the existing SVGs and in a editor find the "feFlood10943" and replace the coloring with that from https://en.wikipedia.org/wiki/User:Benjah-bmm27/MakingMolecules/DSV
by converting the hexcode to decimal RGB. The text can be edited in inkscape or manualy change the text on the second last line of the svg.
```
cd img
python export_svg2png.py 
```
There will be a lot of warnings from the program that the script calls but it should work anyway.
Make a copy of /data/molecule/Br.cml or another atom and adjust it for the new atom. After this molecules will be possible to add in the cmleditor as usual.
