import random, itertools
import pygame

class Reaction:
	def __init__(self, consumed, result):
		self.consumed = consumed
		self.result = result

	"""Sanity check of symbol name, make sure no zeros have been used by mistake"""
	def verify(self, elements):
		for element in elements:
			if 0 in element:
				raise Exception("Tried to create reaction with invalid values")

class Universe:
	__entropy = dict() #Current and shared entropy in the whole universe and all its instances
	"""Universe contains all fundamental particles and laws needed to get the universe to spin"""
	def __init__(self):
		self.__dict = self.__entropy
		self.moelcules = dict()
		self.config = None
		self.link_right = pygame.image.load("img/link-right.png")
		self.link_left = pygame.image.load("img/link-left.png")
		self.link_top = pygame.image.load("img/link-top.png")
		self.link_bottom = pygame.image.load("img/link-bottom.png")
		self.reactions = list()
		self.reactions.append(Reaction(["O","H"], ["OH"]))
		self.reactions.append(Reaction(["O","O"], ["O2"]))
		self.reactions.append(Reaction(["O","H2"], ["H2O"]))
		self.reactions.append(Reaction(["H","H"], ["H2"]))
		self.reactions.append(Reaction(["H","OH"], ["H2O"]))
		self.reactions.append(Reaction(["CH4","H2O"], ["CO"] + 3*["H2"]))
			
	def sublist_in_list(self, sublist, superlist):
		for e in sublist:
			if sublist.count(e) > superlist.count(e):
				return False
		return True

	def reaction_table(self, elem):
		for reaction in self.reactions:
			if self.config.DEBUG: print "if", reaction.consumed, "exists in", elem
			if self.sublist_in_list(reaction.consumed, elem): 
				#all elements needed for the reaction exists in the reacting elements
				print reaction.consumed, "->", reaction.result
				return reaction	
		
		
	def molecule_table(self, molecule):
		layout = dict()
		if molecule == "OH":
			layout[(1,1)] = 'O'	
			layout[(2,1)] = 'H'
		elif molecule == "H2":
			layout[(1,1)] = 'H'	
			layout[(2,1)] = 'H'
		elif molecule == "H2O":
			layout[(1,1)] = 'H'	
			layout[(2,1)] = 'O'
			layout[(3,1)] = 'H'	
		elif molecule == "O2":
			layout[(1,1)] = 'O'	
			layout[(2,1)] = 'O'	
		elif molecule == "CO":
			layout[(1,1)] = 'C'	
			layout[(2,1)] = 'O'
		elif molecule == "CO2":
			layout[(1,1)] = 'O'	
			layout[(2,1)] = 'C'
			layout[(3,1)] = 'O'	
		elif molecule == "CH4":
			layout[(2,2)] = 'C'	
			layout[(2,1)] = 'H'	
			layout[(1,2)] = 'H'	
			layout[(2,3)] = 'H'	
			layout[(3,2)] = 'H'	
		else:
			print "No layout found for:", molecule
			return None
		return layout

	def create_atom(self, symbol, copy=True):
		if not self.moelcules.has_key(symbol):
			self.moelcules[symbol] =  pygame.image.load("img/atom-" + symbol.lower() + ".png")
		if copy:
			return self.moelcules[symbol].copy()
		else:
			return self.moelcules[symbol]
	
	def pos2cord(self, pos):
		x, y = pos
		return (32*(x-1), 32*(y-1))

	def pos2cord_link(self, pos, direction):
		x, y = self.pos2cord(pos)
		if direction == "bottom":
			return (x+1, y+2)
		elif direction == "left":
			return (x-2, y)
				
	def create_links(self, layout):
		links = pygame.Surface((160,160), 0, self.create_atom('O', copy=False))
		for pos in layout.keys():
				x,y = pos
				if layout.has_key((x, y+1)): #Bottom
					link_pos = self.pos2cord_link(pos, "bottom")
					links.blit(self.link_bottom, link_pos)
				if layout.has_key((x-1, y)): #Left
					link_pos = self.pos2cord_link(pos, "left")
					links.blit(self.link_left, link_pos)
		return links

	def create_molecule(self, symbol):
		if self.is_atom(symbol):
			return self.create_atom(symbol)

		layout = self.molecule_table(symbol)
		if layout != None:
			links = self.create_links(layout)
			molecule = pygame.Surface((160,160), 0, links)
			molecule.blit(links, (0,0))
			for pos in layout.keys():
				symbol = layout[pos]
				atom = self.create_atom(symbol, copy=False)
				molecule.blit(atom, self.pos2cord(pos))
			return molecule

	def is_atom(self, symbol):
		if len(symbol) == 1 and symbol.isalpha(): # H, O, F etc.
			return True
		elif len(symbol) == 2 and symbol.isalpha() and symbol[1].islower(): #Fe, Mg, Na etc.
			return True
		elif len(symbol) == 3 and symbol.isalpha() and symbol[1:3].islower(): #Uut, Uup, Uus etc.
			return True
		else:
			return False

	def create_elements(self, elements, pos=None):
		list_of_elements = list()
		if pos != None:
			x, y = pos

		if isinstance(elements, basestring):
			elements = [elements] #elements is a string, wrap it in a list not to confuse for
		for element in elements:
			if pos != None and len(elements) > 1:
				pos = (x + random.randint(-50,50), y + random.randint(-50, 50))
			list_of_elements.append(Element(element, pos))
		return tuple(list_of_elements)
	
	def react(self, elements):
		if len(elements) < 2:
			return
		for perm in itertools.permutations(elements):
			reaction = self.reaction_table(perm)
			if reaction != None:
				print "from:", reaction.consumed, "going to create:", reaction.result
				return reaction 
class Element(pygame.sprite.Sprite):
	"""Element - The universal building block of atoms and molecules"""
	def __init__(self, symbol, pos=None):
		pygame.sprite.Sprite.__init__(self)
		self.universe = Universe()
		self.symbol = symbol
		self.image = self.universe.create_molecule(symbol)
		self.rect = self.image.get_bounding_rect()
		self.active = False
		if pos == None:
			self.rect.move_ip(random.randint(10, 600), random.randint(10, 400))
		else:
			self.rect.move_ip(pos)
				

	def update(self):
		if self.active:	
			pos = pygame.mouse.get_pos()
			self.rect.midtop = pos

	def clicked(self):
		if self.rect.collidepoint(pygame.mouse.get_pos()):
			self.active = True
			return True
		else:
			return False

	def unclicked(self):
		if self.active:
			self.active = False
			return True
		else:
			return False

