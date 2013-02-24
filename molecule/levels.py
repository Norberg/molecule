import pygame
import Universe
import Effects
 
class BaseLevel:
	def __init__(self):
		self.description = None
		self.elements = None
		self.areas = pygame.sprite.Group()
		pass
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
		e =  Universe.universe.create_elements(["H+", "O", "OH-", "O", "H+", "CO2", "CH4"])
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
		e = Universe.universe.create_elements(["H+", "O", "OH-", "O", "H+", "CO2", "CH4"])
		self.elements = pygame.sprite.RenderUpdates(e)
		fire = Effects.Fire((200,100))
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
		e = Universe.universe.create_elements(["H+", "O", "OH-", "O", "H+", "CO2", "CH4"])
		self.elements = pygame.sprite.RenderUpdates(e)
		fire = Effects.Fire((200,100))
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
		e = Universe.universe.create_elements(["H+", "O", "OH-", "O", "H+", "CH4", "O2"])
		self.elements = pygame.sprite.RenderUpdates(e)
		fire = Effects.Fire((200,100))
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
		e = Universe.universe.create_elements(["H+", "O", "OH-", "O", "H+", "NH3", "O2"])
		self.elements = pygame.sprite.RenderUpdates(e)
		fire = Effects.Fire((200,100))
		self.areas = pygame.sprite.RenderUpdates(fire) 
	def check_victory(self):
		to_create = dict()
		to_create["NH4+"] = 1
		return self.match_molecule(self.elements, to_create)
"""	
class Level_6(BaseLevel):
	def __init__(self):
		BaseLevel.__init__(self)
		self.description = "Create a HCL and a Na2SO4 molecule"
		e = Universe.universe.create_elements(["H+", "O", "OH-", "O", "H+", "NaCl", "NaCl", "SO3"])
		self.elements = pygame.sprite.RenderUpdates(e)
		fire = Effects.Fire((200,100), 30000)
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
		e = Universe.universe.create_elements(["P4", "NH3", "NH3", "O", "CO2", "NaCl", "SO3"])
		self.elements = pygame.sprite.RenderUpdates(e)
		fire = Effects.Fire((200,100))
		self.areas = pygame.sprite.RenderUpdates(fire) 
	def check_victory(self):
		to_create = dict()
		to_create["CH4N2O"] = 1 
		return self.match_molecule(self.elements, to_create)	
