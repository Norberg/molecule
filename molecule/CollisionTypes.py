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
import pymunk

WALL = 0b0001
ELEMENT = 0b0010
EFFECT = 0b0100
SCREEN_BOUNDARY = 0b1000

WALL_MASK = WALL | ELEMENT | EFFECT | SCREEN_BOUNDARY
ELEMENT_MASK = WALL | ELEMENT | EFFECT | SCREEN_BOUNDARY
ELEMENT_MASK_DRAGGING = ELEMENT | EFFECT | SCREEN_BOUNDARY
EFFECT_MASK = ELEMENT
SCREEN_BOUNDARY_MASK = WALL | ELEMENT | EFFECT | SCREEN_BOUNDARY

WALL_FILTER = pymunk.ShapeFilter(categories=WALL, mask=WALL_MASK)
ELEMENT_FILTER = pymunk.ShapeFilter(categories=ELEMENT, mask=ELEMENT_MASK)
ELEMENT_FILTER_DRAGGING = pymunk.ShapeFilter(categories=ELEMENT, mask=ELEMENT_MASK_DRAGGING)
EFFECT_FILTER = pymunk.ShapeFilter(categories=EFFECT, mask=EFFECT_MASK)
SCREEN_BOUNDARY_FILTER = pymunk.ShapeFilter(categories=SCREEN_BOUNDARY, mask=SCREEN_BOUNDARY_MASK)