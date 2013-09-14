import glob
import math

import pygame
import pymunk
import pymunk.pygame_util
import Universe
import Effects
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
		self.elements = None
		self.areas = pygame.sprite.Group()
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
		e = Universe.create_elements(self.space,self.cml.molecules)
		self.elements = pygame.sprite.RenderUpdates(e)

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
		self.areas = pygame.sprite.RenderUpdates(new_effects) 

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
