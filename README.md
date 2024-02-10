molecule
========

[![Build Status](https://travis-ci.org/Norberg/molecule.svg?branch=master)](https://travis-ci.org/Norberg/molecule)

Molecule - a chemical reaction puzzle game

Dependencies:
-------
### Game:
* python 3.4, 3.5, 3.6, 3.7
* pyglet 1.4
* pymunk 4.0
* pyglet-gui 0.1
```
curl https://pyenv.run | bash
pyenv install pypy3.7-7.3.9
pyenv virtualenv pypy3.7-7.3.9 venv
pyenv local venv
pip install pyglet==1.2.4
pip install pyglet==1.4.2
pip install pymunk==4
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
