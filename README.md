molecule
========

Molecule - a chemical reaction puzzle game

Dependencies:
-------
### Game:###
* python 2.7
* pygame
* pymunk 4.0

###Cmleditor:###
* python 2.7
* pygtk2
* openbabel (optional, needed to create new molecules)

How to play:
---------
    python start.py --help 
    Molecule - a chemical reaction puzzle game
    -h --help print this help
    --level=LEVEL choose what level to start on
    -d --debug print debug messages
    During gameplay:
    ESC - close game
    r - reset current level
    d - switch Graphic debug on/off
    s - skip level

Structure:
-------
###libcml/###
Library responsible for parsing cml files containing molecules and reactions.

###libreact/###
Library responsible for simulating reactions.

###cmleditor/###
GUI for editing cml files

###molecule/###
Game code.

###data/###
All data for the game.

###tests/###
All testcases for the game.

###img/###
All images.
