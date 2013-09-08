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
import math

import pygame
import pymunk
import Universe
import Effects
import molecule.Config as Config
from molecule import CollisionTypes
 
class BaseLevel:
	def __init__(self):
		self.description = None
		self.elements = None
		self.areas = pygame.sprite.Group()
		self.init_chipmunk()
		
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

	def check_victory(self):
		pass
	def match_molecule(self, elements, to_create):
		for element in elements:
			if to_create.has_key(element.molecule.formula):
				to_create[element.molecule.formula] -= 1
		for element, amount in to_create.iteritems():
			if amount > 0:
				return
		return "victory"
		

class Level_1(BaseLevel):
	def __init__(self):
		BaseLevel.__init__(self)
		self.description = "Create a water molecule"
		#e =  Universe.universe.create_elements(self.space, ["SO3(g)"] +  13*["H2(g)", "P4(g)"] +22* ["CH4(g)"])
		e =  Universe.universe.create_elements(self.space, ["H+(g)", "O(g)", "P(g)", "O(g)", "H+(g)", "F(g)", "Al(s)"])
		self.elements = pygame.sprite.RenderUpdates(e)
	def check_victory(self):
		#Find out if H2O have been created
		for element in self.elements:
			if element.molecule.formula == "H2O":
				return "victory"
class Level_2(BaseLevel):
	def __init__(self):
		BaseLevel.__init__(self)
		self.description = "Create a CO and 3 H2 molecules"
		e = Universe.universe.create_elements(self.space,["H+(g)", "O(g)", "OH-(aq)", "O(g)", "H+(g)", "CO2(g)", "CH4(g)"])
		self.elements = pygame.sprite.RenderUpdates(e)
		fire = Effects.Fire((200,100),self.space)
		self.areas = pygame.sprite.RenderUpdates(fire) 
	def check_victory(self):
		to_create = dict()
		to_create["CO"] = 1
		to_create["H2"] =  3
		return self.match_molecule(self.elements, to_create)	
				
class Level_3(BaseLevel):
	def __init__(self):
		BaseLevel.__init__(self)
		self.description = "Create a CO and 3 H20 molecules"
		e = Universe.universe.create_elements(self.space,["H+(g)", "O(g)", "OH-(aq)", "O(g)", "H+(g)", "CO2(g)", "CH4(g)"])
		self.elements = pygame.sprite.RenderUpdates(e)
		fire = Effects.Fire((200,100),self.space)
		self.areas = pygame.sprite.RenderUpdates(fire) 
	def check_victory(self):
		to_create = dict()
		to_create["CO"] = 1
		to_create["H2O"] = 3 
		return self.match_molecule(self.elements, to_create)	

class Level_4(BaseLevel):
	def __init__(self):
		BaseLevel.__init__(self)
		self.description = "Create a CO2 and 2 H20 molecules"
		e = Universe.universe.create_elements(self.space,["H+(g)", "O(g)", "OH-(aq)", "O(g)", "H+(g)", "CH4(g)", "O2(g)"])
		self.elements = pygame.sprite.RenderUpdates(e)
		fire = Effects.Fire((200,100),self.space)
		self.areas = pygame.sprite.RenderUpdates(fire) 
	def check_victory(self):
		to_create = dict()
		to_create["CO2"] = 1
		to_create["H2O"] = 2 
		return self.match_molecule(self.elements, to_create)	
""" this reaction is not possible until cold is supported
class Level_5(BaseLevel):
	def __init__(self):
		BaseLevel.__init__(self)
		self.description = "Create a NH4+ molecule"
		e = Universe.universe.create_elements(self.space,["H+(g)", "O(g)", "OH-(aq)", "O(g)", "H+(g)", "NH3(g)", "O2(g)"])
		self.elements = pygame.sprite.RenderUpdates(e)
		fire = Effects.Fire((200,100),self.space)
		self.areas = pygame.sprite.RenderUpdates(fire) 
	def check_victory(self):
		to_create = dict()
		to_create["NH4+(g)"] = 1
		return self.match_molecule(self.elements, to_create)
"""	
class Level_6(BaseLevel):
	def __init__(self):
		BaseLevel.__init__(self)
		self.description = "Create a HCL and a Na2SO4 molecule"
		e = Universe.universe.create_elements(self.space,["H+(g)", "O(g)", "OH-(aq)", "O(g)", "H+(g)", "NaCl(s)", "NaCl(s)", "SO3(g)"])
		self.elements = pygame.sprite.RenderUpdates(e)
		fire = Effects.Fire((200,100),self.space, 30000)
		self.areas = pygame.sprite.RenderUpdates(fire) 
	def check_victory(self):
		to_create = dict()
		to_create["HCl"] = 1
		to_create["Na2SO4"] = 1 
		return self.match_molecule(self.elements, to_create)	

class Level_7(BaseLevel):
	def __init__(self):
		BaseLevel.__init__(self)
		self.description = "Create a CH4NO2 molecule"
		e = Universe.universe.create_elements(self.space,["P4(g)", "NH3(g)", "NH3(g)", "O(g)", "CO2(g)", "NaCl(s)", "SO3(g)"])
		self.elements = pygame.sprite.RenderUpdates(e)
		fire = Effects.Fire((200,100),self.space)
		self.areas = pygame.sprite.RenderUpdates(fire) 
	def check_victory(self):
		to_create = dict()
		to_create["CH4N2O"] = 1 
		return self.match_molecule(self.elements, to_create)	

class Level_8(BaseLevel):
	def __init__(self):
		BaseLevel.__init__(self)
		self.description = "Create a CaCO3 molecule"
		e = Universe.universe.create_elements(self.space,["O2(g)", "O2(g)", "O2(g)", "N(g)", "N(g)", "O(g)", "CaO2H2(s)", "Na2CO3(s)", "SO3(g)", "H2(g)", "H2(g)", "H2(g)"])
		self.elements = pygame.sprite.RenderUpdates(e)
		fire = Effects.Fire((200,100), self.space)
		water = Effects.Water_Beaker((650,400), self.space)
		self.areas = pygame.sprite.RenderUpdates((fire,water)) 
	def check_victory(self):
		to_create = dict()
		to_create["CaCO3"] = 1 
		return self.match_molecule(self.elements, to_create)

class Level_9(BaseLevel):
	def __init__(self):
		BaseLevel.__init__(self)
		self.description = "Create a CaCO3 molecule"
		e = Universe.universe.create_elements(self.space,["O2(g)", "O2(g)", "H2O(l)", "Na3PO4(s)", "CuSO4(s)"])
		self.elements = pygame.sprite.RenderUpdates(e)
		fire = Effects.Fire((200,100), self.space)
		water = Effects.Water_Beaker((650,400), self.space)
		self.areas = pygame.sprite.RenderUpdates((fire,water)) 
	def check_victory(self):
		to_create = dict()
		to_create["CaCO3"] = 2 
		return self.match_molecule(self.elements, to_create)
