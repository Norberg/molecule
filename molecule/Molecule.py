import random
import pymunk
import pygame
import PyGameUtil,util,Bonds
import molecule.Config as Config
from pymunk.vec2d import Vec2d

class Molecule:
	ATOM_SIZE = 32
	BOND_LENGHT = 6
	MOLECULE_MAX_SIZE = 300
	def __init__(self,formula, enthalpy = 0, entropy = 0, mass = 10):
		self.formula = formula
		self.atom_layout = dict()
		self.bond_layout = list()
		self.sprite = None
		self.enthalpy = enthalpy # aka H
		self.entropy = entropy # aka S
		self.mass = mass
		
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

class MoleculeSprite(pygame.sprite.Sprite):
	def __init__(self, molecule, space, pos=None):
		pygame.sprite.Sprite.__init__(self)
		self.molecule = molecule
		self.image = self.molecule.createMoleculeSprite()
		self.rect = self.image.get_bounding_rect()
		self.active = False
		self.init_chipmunk(space)
		if pos == None:
			self.move((random.randint(10, 600), random.randint(10, 400)))
		else:
			self.move(pos)
				
	def init_chipmunk(self,space):	
		body = pymunk.Body(10,pymunk.moment_for_circle(10, 0, 16))
		shape = pymunk.Circle(body, 16)
		space.add(shape, body)
		self.shape = shape
		self.shape.elasticity = 0.95
		x = random.randrange(-10, 10)/10.0
		y = random.randrange(-10, 10)/10.0
		vec = Vec2d(x,y)
		force = 3000
		body.apply_impulse(force * vec)		

	def move(self, pos):
		self.rect.center = pos
		self.shape.body.position = pymunk.pygame_util.from_pygame(pos, Config.current.screen)
		
	def update(self):
		if self.active:
			old_pos = self.rect.center
			pos = pygame.mouse.get_pos()
			self.move(pos)
			self.shape.body.velocity = Vec2d(pos) - Vec2d(old_pos)
			self.shape.body.mass = 1000
		else:
			self.rect.center =  pymunk.pygame_util.to_pygame(self.shape.body.position, Config.current.screen)

	def clicked(self):
		if self.rect.collidepoint(pygame.mouse.get_pos()):
			self.active = True
			return True
		else:
			return False

	def unclicked(self):
		if self.active:
			self.active = False
			self.shape.body.velocity = Vec2d(0,0)
			self.shape.body.mass = self.molecule.mass
			return True
		else:
			return False

