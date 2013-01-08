import pygame
from Universe import Universe

class BaseLevel:
	def __init__(self):
		self.universe = Universe()
		self.description = None
		self.elements = None
		pass
	def check_victory(self):
		pass
	def match_molecule(self, elements, to_create):
		for element in elements:
			if to_create.has_key(element.symbol):
				to_create[element.symbol] -= 1
		for element, amount in to_create.iteritems():
			if amount > 0:
				return
		return "victory"
		

class Level_1(BaseLevel):
	def __init__(self):
		BaseLevel.__init__(self)
		self.description = "Create a water molecule"
		e =  self.universe.create_elements(["H", "O", "OH", "O", "H", "CO2", "CH4"])
		self.elements = pygame.sprite.RenderUpdates(e)
	def check_victory(self):
		#Find out if H2O have been created
		for element in self.elements:
			if element.symbol == "H2O":
				return "victory"
class Level_2(BaseLevel):
	def __init__(self):
		BaseLevel.__init__(self)
		self.description = "Create a CO and 3 H2 molecules"
		e =  self.universe.create_elements(["H", "O", "OH", "O", "H", "CO2", "CH4"])
		self.elements = pygame.sprite.RenderUpdates(e)
	def check_victory(self):
		to_create = dict()
		to_create["CO"] = 1
		to_create["H2"] =  3
		return self.match_molecule(self.elements, to_create)	
				
