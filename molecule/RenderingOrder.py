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
import pyglet

# In pyglet 2+, OrderedGroup is replaced with Group
background = pyglet.graphics.Group(0)
hud = pyglet.graphics.Group(1)
state = pyglet.graphics.Group(2)
# Bonds should render beneath atom sprites so atoms draw on top.
bonds = pyglet.graphics.Group(3)
elements = pyglet.graphics.Group(4)
charge = pyglet.graphics.Group(5)
gui_background = pyglet.graphics.Group(6)  # GUI backgrounds render first
gui = pyglet.graphics.Group(7)  # GUI text and elements render on top
