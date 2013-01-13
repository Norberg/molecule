import pygame
from Universe import Universe, Fire

class BaseLevel:
	def __init__(self):
		self.universe = Universe()
		self.description = None
		self.elements = None
		self.areas = pygame.sprite.Group()
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
		e =  self.universe.create_elements(["H+", "O-2", "OH-", "O-2", "H+", "CO2", "CH4"])
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
		e =  self.universe.create_elements(["H+", "O-2", "OH-", "O-2", "H+", "CO2", "CH4"])
		self.elements = pygame.sprite.RenderUpdates(e)
		fire = Fire((200,100))
		self.areas = pygame.sprite.RenderUpdates(fire) 
	def check_victory(self):
		to_create = dict()
		to_create["CO-"] = 1
		to_create["H2"] =  3
		return self.match_molecule(self.elements, to_create)	
				
class Level_3(BaseLevel):
	def __init__(self):
		BaseLevel.__init__(self)
		self.description = "Create a CO and 3 H20 molecules"
		e =  self.universe.create_elements(["H+", "O-2", "OH-", "O-2", "H+", "CO2", "CH4"])
		self.elements = pygame.sprite.RenderUpdates(e)
		fire = Fire((200,100))
		self.areas = pygame.sprite.RenderUpdates(fire) 
	def check_victory(self):
		to_create = dict()
		to_create["CO-"] = 1
		to_create["H2O"] = 3 
		return self.match_molecule(self.elements, to_create)	

class Level_4(BaseLevel):
	def __init__(self):
		BaseLevel.__init__(self)
		self.description = "Create a CO2 and 2 H20 molecules"
		e =  self.universe.create_elements(["H+", "O-2", "OH-", "O-2", "H+", "CH4", "O2"])
		self.elements = pygame.sprite.RenderUpdates(e)
		fire = Fire((200,100))
		self.areas = pygame.sprite.RenderUpdates(fire) 
	def check_victory(self):
		to_create = dict()
		to_create["CO2"] = 1
		to_create["H2O"] = 2 
		return self.match_molecule(self.elements, to_create)	
