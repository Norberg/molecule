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
sudo apt install build-essential libffi-dev libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev curl \
    llvm libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev \
    liblzma-dev
curl https://pyenv.run | bash
pyenv install 3.8.18
pyenv virtualenv 3.8.18 venv-molecule
pyenv activate venv-molecule
pip install pyglet==1.5.16
pip install pymunk==6.6
pip install --upgrade pip setuptools wheel
pip install git+https://github.com/jorgecarleitao/pyglet-gui.git
```

### Cmleditor:
* python 3
* PyGObject
* GTK+3
* openbabel (optional, needed to create new molecules)
* rdkit (optional, needed to create new molecules and reactions)
```
sudo apt install libgirepository1.0-dev openbabel
pip install rdkit 
pip install pygobject 
```


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





#### Adding a new atom
Copy one of the existing SVGs and in a editor find the "feFlood10943" and replace the coloring with that from https://en.wikipedia.org/wiki/User:Benjah-bmm27/MakingMolecules/DSV
by converting the hexcode to decimal RGB. The text can be edited in inkscape or manualy change the text on the second last line of the svg.
```
cd img
python export_svg2png.py 
```
There will be a lot of warnings from the program that the script calls but it should work anyway.
Make a copy of /data/molecule/Br.cml or another atom and adjust it for the new atom. After this molecules will be possible to add in the cmleditor as usual.
