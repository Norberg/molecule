import glob, random
import pygame

class Reaction:
	def __init__(self, consumed, result, areas = list()):
		self.verify(consumed)
		self.verify(result)
		self.consumed = consumed
		self.result = result
		self.areas = areas

	"""Sanity check of symbol name, make sure no zeros have been used by mistake"""
	def verify(self, elements):
		for element in elements:
			if "0" in element:
				raise Exception("Tried to create reaction with invalid values")
class Molecule:
	def __init__(self,formula):
		self.formula = formula
		self.atom_layout = dict()
		self.bond_layout = list()

	def addAtom(self, pos_x, pos_y, atom):
		self.atom_layout[(pos_x, pos_y)] = atom

	def addAtoms(self,matrix):
		row_nr = 1
		for row in matrix:
			collum_nr = 1
			for collum in row:
				if len(collum.strip()) != 0:
					self.addAtom(collum_nr, row_nr, collum)
				collum_nr += 1
			row_nr += 1 	
	
	def addBond(self, from_pos, to_pos, nr_of_bonds = 1):
		self.bond_layout.append(Bond(from_pos, to_pos, nr_of_bonds))
		self.bond_layout.append(Bond(to_pos, from_pos, nr_of_bonds))
	
	def autoBonds(self):
		for pos in self.atom_layout.keys():
			x,y = pos
			if self.atom_layout.has_key((x, y+1)): #Bottom
				self.addBond(pos, (x,y+1))
			if self.atom_layout.has_key((x+1, y)): #Right
				self.addBond(pos, (x+1,y))

class Bond:
	def __init__(self, from_pos, to_pos, nr_of_bonds = 1):
		self.from_pos = from_pos
		self.to_pos = to_pos
		self.nr_of_bonds = nr_of_bonds

class BondImage:
	def __init__(self, path, is_vertical=False):
		self.bond = list()
		self.bond.append(pygame.image.load(path))
		
		if is_vertical:
			b2pos1 = (-3,0)
			b2pos2 = (3,0)
			b3pos1 = (-5,0)
			b3pos2 = (0,0)
			b3pos3 = (5,0)
		else:
			b2pos1 = (0,-3)
			b2pos2 = (0,3)
			b3pos1 = (0,-5)
			b3pos2 = (0,0)
			b3pos3 = (0,5)
				
		b = pygame.Surface((64,64), 0, self.get(1))
		b.blit(self.get(1), b2pos1)
		b.blit(self.get(1), b2pos2)
		self.bond.append(b)

		b = pygame.Surface((64,64), 0, self.get(1))
		b.blit(self.get(1), b3pos1)
		b.blit(self.get(1), b3pos2)
		b.blit(self.get(1), b3pos3)
		self.bond.append(b)

	def get(self, bond):
		return self.bond[bond-1]		
		
		

class Universe:
	ATOM_SIZE = 32
	BOND_LENGHT = 6
	MOLECULE_MAX_SIZE = (300,300)
	__entropy = dict() #Current and shared entropy in the whole universe and all its instances
	"""Universe contains all fundamental particles and laws needed to get the universe to spin"""
	def __init__(self):
		self.__dict = self.__entropy
		self.moelcules = dict()
		self.config = None
		self.__init__bonds()
		self.__init__molecule_table()
		self.__init__reactions()

	def __init__bonds(self):
		self.bond_horizontal = BondImage("img/bond-horizontal.png")
		self.bond_vertical = BondImage("img/bond-vertical.png", is_vertical = True)
		self.bond_northwest = BondImage("img/bond-northwest.png")
		self.bond_southwest = BondImage("img/bond-southwest.png")
		
	def __init__reactions(self):
		self.reactions = list()
		self.reactions.append(Reaction(["O-2","H+"], ["OH-"]))
		self.reactions.append(Reaction(["O-2","O-2"], ["O2"]))
		self.reactions.append(Reaction(["O-2","H2"], ["H2O"]))
		self.reactions.append(Reaction(["H+","H+"], ["H2"]))
		self.reactions.append(Reaction(["H+","OH-"], ["H2O"]))
		self.reactions.append(Reaction(["CH4","H2O"], ["CO-"] + 3*["H2"],["Fire"]))
		self.reactions.append(Reaction(["CH4"] + 2*["O2"], ["CO2"] + 2*["H2O"],["Fire"]))
		self.reactions.append(Reaction(["CH4", "O2"], ["CO-"] + 2*["H2O"],["Fire"]))
		self.reactions.append(Reaction(["NH3", "H2O"], ["NH4+"] + ["OH-"]))
		self.reactions.append(Reaction(["SO3", "H2O"], ["H2SO4"]))
		self.reactions.append(Reaction(["H2SO4"] + 2*["NaCl"], 2*["HCl"] + ["Na2SO4"]))

	def __init__molecule_table(self):
		self.molecule_layouts = dict()
		m = Molecule("OH-")
		m.addAtoms([['O','H-']])
		self.add_molecule_layout(m)

		m = Molecule("H2")
		m.addAtoms([['H','H']])
		self.add_molecule_layout(m)

		m = Molecule("H2O")
		m.addAtoms([['H','O','H']])
		self.add_molecule_layout(m)
		
		m = Molecule("O2")
		m.addAtoms([['O','O']])
		m.addBond((1,1),(2,1),2)
		self.add_molecule_layout(m)
		
		m = Molecule("CO-")
		m.addAtoms([['C','O-']])
		m.addBond((1,1),(2,1),2)
		self.add_molecule_layout(m)
		
		m = Molecule("CO2")
		m.addAtoms([['O','C','O']])
		m.addBond((1,1),(2,1),2)
		m.addBond((2,1),(3,1),2)
		self.add_molecule_layout(m)
		
		m = Molecule("CH4")
		m.addAtoms([[' ','H',' '],
                            ['H','C','H'],
                            [' ','H',' ']])
		self.add_molecule_layout(m)
		
		m = Molecule("NH3")
		m.addAtoms([['H',' ','H'],
                            [' ','N',' '],
                            [' ','H',' ']])
		m.autoBonds()
		m.addBond((1,1),(2,2))
		m.addBond((3,1),(2,2))
		self.add_molecule_layout(m)

		m = Molecule("NH4+")
		m.addAtoms([[' ','H' ,' '],
                            ['H','N+','H'],
                            [' ','H' ,' ']])
		self.add_molecule_layout(m)
		
		m = Molecule("HCl")
		m.addAtoms([['H','Cl']])
		self.add_molecule_layout(m)
		
		m = Molecule("NaCl")
		m.addAtoms([['Na','Cl']])
		self.add_molecule_layout(m)
		
		m = Molecule("HCl")
		m.addAtoms([['H','Cl']])
		self.add_molecule_layout(m)
		
		m = Molecule("SO3")
		m.addAtoms([['O',' ','O'],
                            [' ','S',' '],
                            [' ','O',' ']])
		m.autoBonds()
		m.addBond((1,1),(2,2),2)
		m.addBond((3,1),(2,2),2)
		m.addBond((2,3),(2,2),2)
		self.add_molecule_layout(m)

		m = Molecule("SO4+")
		m.addAtoms([[' ','O' ,' '],
                            ['O','S+','O'],
                            [' ','O' ,' ']])
		self.add_molecule_layout(m)
		
		m = Molecule("H2SO4")
		m.addAtoms([[' ',' ','O' ,' ',' '],
                            ['H','O','S+','O','H'],
                            [' ',' ','O' ,' ',' ']])
		m.autoBonds()
		m.addBond((3,1),(3,2),2)
		m.addBond((3,3),(3,2),2)
		self.add_molecule_layout(m)
		
		m = Molecule("Na2SO4")
		m.addAtoms([[' ', 'O', ' ','Na'],
                            ['O', 'S+','O',' '],
                            [' ', 'O', ' ',' '],
                            ['Na',' ', ' ',' ']])
		m.autoBonds()
		m.addBond((2,1),(2,2),2)
		m.addBond((1,2),(2,2),2)
		m.addBond((1,4),(2,3))
		m.addBond((4,1),(3,2))
		self.add_molecule_layout(m)
			
	def sublist_in_list(self, sublist, superlist):
		for e in sublist:
			if sublist.count(e) > superlist.count(e):
				return False
		return True

	def reaction_table(self, elem, areas):
		for reaction in self.reactions:
			if self.config.DEBUG: print "if", reaction.consumed, "exists in", elem
			if self.sublist_in_list(reaction.consumed, elem):
				#all elements needed for the reaction exists in the reacting elements
				if self.sublist_in_list(reaction.areas, areas):
					#all areas need for reaction was present
					print reaction.consumed, "+", areas, "->", reaction.result
					return reaction	
		
	def add_molecule_layout(self, molecule):
		if len(molecule.bond_layout) == 0:
			molecule.autoBonds()
		self.molecule_layouts[molecule.formula] = molecule
			
				
	def molecule_table(self, molecule):
		if self.molecule_layouts.has_key(molecule):
			return self.molecule_layouts[molecule]
		else:
			raise Exception("No layout found for:" + molecule)

	def get_electric_charge(self, symbol):
		value = 0
		if symbol.count("-") == 1:
			v = symbol.split("-")[1]
			if v == "":
				value = -1
			else:
				value = -int(v)

		elif symbol.count("+") == 1:
			v = symbol.split("+")[1]
			if v == "":
				value = 1
			else:
				value = int(v)
		return value	

	def create_atom(self, symbol, copy=True):
		if not self.moelcules.has_key(symbol):
			no_charge = self.get_only_atom_symbol(symbol)
			a =  pygame.image.load("img/atom-" + no_charge.lower() + ".png")
			atom = pygame.Surface(self.MOLECULE_MAX_SIZE, 0, a)
			atom.blit(a, (0,0))
			charge = self.get_electric_charge(symbol)
			if charge == 0:
				pass
			elif charge == -1:
				atom.blit(pygame.image.load("img/e-1.png"), (0,0))
			elif charge == -2:
				atom.blit(pygame.image.load("img/e-2.png"), (0,0))
			elif charge == 1:
				atom.blit(pygame.image.load("img/e+1.png"), (0,0))
			elif charge == 2:
				atom.blit(pygame.image.load("img/e+2.png"), (0,0))
			self.moelcules[symbol] = atom		
		if copy:
			return self.moelcules[symbol].copy()
		else:
			return self.moelcules[symbol]
	
	def pos2cord(self, pos):
		spacing = self.ATOM_SIZE + self.BOND_LENGHT/2	
		x, y = pos
		return (spacing*(x-1),spacing*(y-1))

	def create_bonds(self, molecule):
		bonds = pygame.Surface((self.MOLECULE_MAX_SIZE), 0, self.create_atom('O', copy=False))
		for bond in molecule.bond_layout:
				x,y = bond.from_pos
				bond_pos = self.pos2cord(bond.from_pos)
				bond_nr = bond.nr_of_bonds
				if bond.to_pos == (x,y+1): #South
					bonds.blit(self.bond_vertical.get(bond_nr), bond_pos)
				elif bond.to_pos == (x+1, y): #West
					bonds.blit(self.bond_horizontal.get(bond_nr), bond_pos)
				elif bond.to_pos == (x+1,y-1): #NorthWest
					bond_pos = self.pos2cord((x,y-1))
					bonds.blit(self.bond_northwest.get(bond_nr), bond_pos)
				elif bond.to_pos == (x+1,y+1): #SouthWest
					bonds.blit(self.bond_southwest.get(bond_nr), bond_pos)
					
		return bonds

	def create_molecule(self, symbol):
		if self.is_atom(symbol):
			return self.create_atom(symbol)

		m = self.molecule_table(symbol)
		layout = m.atom_layout
		if layout != None:
			bonds = self.create_bonds(m)
			molecule = pygame.Surface(self.MOLECULE_MAX_SIZE, 0, bonds)
			molecule.blit(bonds, (0,0))
			for pos in layout.keys():
				symbol = layout[pos]
				atom = self.create_atom(symbol, copy=False)
				molecule.blit(atom, self.pos2cord(pos))
			return molecule
		else:
			raise Exception("Failed to generate: " + symbol)

	#returns the atom symbol without any electric charge
	def get_only_atom_symbol(self, symbol):
		return symbol.split("-")[0].split("+")[0]

	def is_atom(self, symbol):
		symbol = symbol.split("-")[0].split("+")[0] #Remove +/-
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
	
	def react(self, elements, areas):
		if len(elements) < 2:
			return
		if self.config.DEBUG: print "Trying to see if some of this react:", elements
		reaction = self.reaction_table(elements, areas)
		if reaction != None:
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

class Fire(pygame.sprite.Sprite):
	"""Fire"""
	def __init__(self, pos):
		pygame.sprite.Sprite.__init__(self)
		self.name = "Fire"
		self.current_frame = 0
		self.frames = 50
		self.animations = list()
		for img in sorted(glob.glob("img/fire/50 frames/*")):
			self.animations.append(pygame.image.load(img))
		self.image = self.animations[self.current_frame]
		self.rect = self.image.get_bounding_rect()
		self.rect.move_ip(pos)
				

	def update(self):
		self.current_frame += 1
		if self.current_frame >= self.frames:
			self.current_frame = 0

		self.image = self.animations[self.current_frame]
