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

__img_cache = dict()
def loadImage(src):
	global __img_cache
	if src in __img_cache:
		return __img_cache[src]
	img = pyglet.image.load(src)
	__img_cache[src] = img
	return __img_cache[src]

__object_cache = dict()

def storeObject(key, obj):
	global __object_cache
	__object_cache[key] = obj

def getObject(key):
	return __object_cache[key]

def hasObject(key):
	return key in __object_cache

