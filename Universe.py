import glob, random
import pygame
import PyGameUtil,util,Bonds

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
	ATOM_SIZE = 32
	BOND_LENGHT = 6
	MOLECULE_MAX_SIZE = 300
	def __init__(self,formula):
		self.formula = formula
		self.atom_layout = dict()
		self.bond_layout = list()
		self.sprite = None
		
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
		self.bond_layout.append(Bonds.Bond(from_pos, to_pos, nr_of_bonds))
		self.bond_layout.append(Bonds.Bond(to_pos, from_pos, nr_of_bonds))
	
	def autoBonds(self):
		for pos in self.atom_layout.keys():
			x,y = pos
			if self.atom_layout.has_key((x, y+1)): #Bottom
				self.addBond(pos, (x,y+1))
			if self.atom_layout.has_key((x+1, y)): #Right
				self.addBond(pos, (x+1,y))

	def createMoleculeSprite(self):
		if util.isAtom(self.formula):
			return self.createAtomSprite(self.formula)

		bond = self.createBonds()
		self.sprite = PyGameUtil.createSurface(self.MOLECULE_MAX_SIZE)
		self.sprite.blit(bond, (0,0))
		for pos, symbol in self.atom_layout.iteritems():
			atom = self.createAtomSprite(symbol)
			self.sprite.blit(atom, self.pos2cord(pos))
		return self.sprite
	
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

	def createAtomSprite(self,symbol):
		if PyGameUtil.hasObject(symbol):
			atom =  PyGameUtil.getObject(symbol)
		else:
			no_charge = self.get_only_atom_symbol(symbol)
			atom =  PyGameUtil.loadImage("img/atom-" + no_charge.lower() + ".png").copy()
			charge = self.get_electric_charge(symbol)
			if charge == 0:
				pass
			elif charge == -1:
				atom.blit(PyGameUtil.loadImage("img/e-1.png"), (0,0))
			elif charge == -2:
				atom.blit(PyGameUtil.loadImage("img/e-2.png"), (0,0))
			elif charge == 1:
				atom.blit(PyGameUtil.loadImage("img/e+1.png"), (0,0))
			elif charge == 2:
				atom.blit(PyGameUtil.loadImage("img/e+2.png"), (0,0))
			PyGameUtil.storeObject(symbol, atom)
		return atom
	
	def pos2cord(self, pos):
		spacing = self.ATOM_SIZE + self.BOND_LENGHT/2	
		x, y = pos
		return (spacing*(x-1),spacing*(y-1))

	def createBonds(self):
		bonds = PyGameUtil.createSurface(self.MOLECULE_MAX_SIZE)
		for bond in self.bond_layout:
				x,y = bond.from_pos
				bond_pos = self.pos2cord(bond.from_pos)
				bond_nr = bond.nr_of_bonds
				if bond.to_pos == (x,y+1): #South
					bonds.blit(Bonds.vertical.get(bond_nr), bond_pos)
				elif bond.to_pos == (x+1, y): #West
					bonds.blit(Bonds.horizontal.get(bond_nr), bond_pos)
				elif bond.to_pos == (x+1,y-1): #NorthWest
					bond_pos = self.pos2cord((x,y-1))
					bonds.blit(Bonds.northwest.get(bond_nr), bond_pos)
				elif bond.to_pos == (x+1,y+1): #SouthWest
					bonds.blit(Bonds.southwest.get(bond_nr), bond_pos)
					
		return bonds


	""" returns the atom symbol without any electric charge """
	def get_only_atom_symbol(self, symbol):
		return symbol.split("-")[0].split("+")[0]



class Universe:
	__entropy = dict() #Current and shared entropy of the whole universe and all its instances
	"""Universe contains all fundamental particles and laws needed to get the universe to spin"""
	def __init__(self):
		self.__dict = self.__entropy
		self.moelcules = dict()
		self.config = None
		self.__init__molecule_table()
		self.__init__reactions()
		Bonds.init__bonds()

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
		
		m = Molecule("P4")
		m.addAtoms([[' ','P',' ','P'],
                            ['P',' ','P',' ']])
		m.addBond((1,2),(2,1),3)
		m.addBond((2,1),(3,2),2)
		m.addBond((3,2),(4,1),3)
		self.add_molecule_layout(m)
			

	def reaction_table(self, elem, areas):
		for reaction in self.reactions:
			if self.config.DEBUG: print "if", reaction.consumed, "exists in", elem
			if util.sublist_in_list(reaction.consumed, elem):
				#all elements needed for the reaction exists in the reacting elements
				if util.sublist_in_list(reaction.areas, areas):
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
		elif util.isAtom(molecule):
			return Molecule(molecule)
		else:
			raise Exception("No layout found for:" + molecule)
	
	def create_elements(self, elements, pos=None):
		list_of_elements = list()
		if pos != None:
			x, y = pos

		if isinstance(elements, basestring):
			elements = [elements] #elements is a string, wrap it in a list not to confuse for
		for element in elements:
			if pos != None and len(elements) > 1:
				pos = (x + random.randint(-50,50), y + random.randint(-50, 50))
			molecule = self.molecule_table(element)
			list_of_elements.append(Element(molecule, pos))
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
	def __init__(self, molecule, pos=None):
		pygame.sprite.Sprite.__init__(self)
		self.universe = Universe()
		self.molecule = molecule
		self.image = self.molecule.createMoleculeSprite()
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
			self.animations.append(PyGameUtil.loadImage(img))
		self.image = self.animations[self.current_frame]
		self.rect = self.image.get_bounding_rect()
		self.rect.move_ip(pos)
				

	def update(self):
		self.current_frame += 1
		if self.current_frame >= self.frames:
			self.current_frame = 0

		self.image = self.animations[self.current_frame]
