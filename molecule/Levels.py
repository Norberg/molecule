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
import glob
import math

import pyglet
import pymunk
import pymunk.pygame_util
from molecule import Universe
from molecule import Effects
from molecule import Config
from molecule import CollisionTypes
from libcml import Cml

class Levels:
	def __init__(self, path):
		self.path = path
		self.init_levels()
		self.current_level = -1

	def init_levels(self):
		filenames = glob.glob(self.path+"/*")
		#files that contatins # is disabled
		self.levels = [name for name in filenames if not '#' in name]
		self.levels.sort()
	
	def next_level(self):
		self.current_level += 1
		if self.current_level >= len(self.levels):
			return None
		path = self.levels[self.current_level]
		cml = Cml.Level()
		cml.parse(path)
		return Level(cml)

	def level_iter(self):
		level = self.next_level()
		while level is not None:
			yield level
			level = self.next_level()

class Level:
	def __init__(self, cml):
		self.cml = cml
		self.batch = pyglet.graphics.Batch()
		self.background_group = pyglet.graphics.OrderedGroup(0)
		self.elements_group = pyglet.graphics.OrderedGroup(1)
		self.init_chipmunk()
		self.init_elements()
		self.init_effects()
	
	def init_chipmunk(self):
		self.space = pymunk.Space()
		self.space.idle_speed_threshold = 0.5
		#self.space.collision_slop = 0.05
		#self.space.collision_bias = math.pow(1.0 - 0.3, 60.0)
		#self.space.gravity = (0.0, -500.0)
		thicknes = 100
		offset = thicknes#/2
		max_x = Config.current.screenSize[0] + offset
		max_y = Config.current.screenSize[1] + offset
		walls = [pymunk.Segment(self.space.static_body, (-offset,-offset), (max_x, -offset), thicknes),
		         pymunk.Segment(self.space.static_body, (-offset, -offset), (-offset, max_y), thicknes),
		         pymunk.Segment(self.space.static_body, (-offset, max_y), (max_x, max_y), thicknes),
		         pymunk.Segment(self.space.static_body, (max_x, max_y), (max_x, -offset), thicknes)
                ]
		for wall in walls:
			wall.elasticity = 0.95
			wall.collision_type = CollisionTypes.WALL
		self.space.add(walls)
	
	def init_elements(self):	
		self.elements = Universe.create_elements(self.space, self.cml.molecules,
		                                  self.batch, self.elements_group)

	def init_effects(self):
		new_effects = list()
		for effect in self.cml.effects:
			if effect.title == "Fire":
				x = effect.x2
				y = effect.y2
				value = effect.value
				fire = Effects.Fire((x,y), self.space, value)
				new_effects.append(fire)
			elif effect.title == "WaterBeaker":
				x = effect.x2
				y = effect.y2
				water = Effects.Water_Beaker((x, y), self.space)
				new_effects.append(water)
		self.areas = new_effects
	
	def update(self):
		"""Update pos of all included elements"""
		for element in self.elements:
			element.update()

	def reset(self):
		self.__init__(self.cml)

	def check_victory(self):
		to_check = list(self.cml.victory_condition)
		for element in self.elements:
			if element.molecule.formula in to_check:
				to_check.remove(element.molecule.formula)
		
		if len(to_check) == 0:
			return True
		else:
			return False
