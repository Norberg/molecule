# Molecule - a chemical reaction puzzle game
# Copyright (C) 2013 Simon Norberg <simon@pthread.se>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import os
from pyglet.resource import Loader

loader = Loader("img", script_home=os.getcwd())

def load_image(name):
    img = loader.image(name)
    return img

def clicked(pos, sprite):
    return pos_inside(pos, sprite.position, sprite.width, sprite.height)

def pos_inside(pos, rec_pos, rec_width, rec_height):
    x, y = pos
    rec_x, rec_y = rec_pos
    rec_X = rec_x + rec_width
    rec_Y = rec_y + rec_height
    return between(x, rec_x, rec_X) and between(y, rec_y, rec_Y)

def between(a, b, B):
    return a >= b and a <= B
