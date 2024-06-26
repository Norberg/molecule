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

background = pyglet.graphics.OrderedGroup(0)
hud = pyglet.graphics.OrderedGroup(1)
state = pyglet.graphics.OrderedGroup(2)
elements = pyglet.graphics.OrderedGroup(3)
charge = pyglet.graphics.OrderedGroup(4)
gui = pyglet.graphics.OrderedGroup(5)
