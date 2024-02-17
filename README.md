molecule
========

[![Build Status](https://travis-ci.org/Norberg/molecule.svg?branch=master)](https://travis-ci.org/Norberg/molecule)

Molecule - a chemical reaction puzzle game

Dependencies:
-------
### Game:
* python 3.8
* pyglet 1.5
* pymunk 6.6
* pyglet-gui 0.1
```
curl https://pyenv.run | bash
pyenv install 3.8.18
pyenv virtualenv 3.8.18 venv-molecule
pyenv activate venv-molecule
pip install pyglet==1.5
pip install pymunk==6.6
pip install git+https://github.com/jorgecarleitao/pyglet-gui.git
```

### Cmleditor:
* python 3
* PyGObject
* GTK+3
* openbabel (optional, needed to create new molecules)

How to play:
---------
    python start.py --help
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
