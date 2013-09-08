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
import random
import pymunk
import pygame
import PyGameUtil,util
import molecule.Config as Config
from molecule import CollisionTypes
from pymunk.vec2d import Vec2d
from libcml import Cml
from libcml import CachedCml
from libreact import Reaction

class Molecule:
	ATOM_SIZE = 32
	BOND_LENGHT = 6
	MOLECULE_MAX_SIZE = 150
	def __init__(self, formula_with_state):
		formula, state = Reaction.split_state(formula_with_state)
		self.formula = formula
		self.current_state = state
		self.cml = CachedCml.getMolecule(formula)
		self.cml.normalize_pos()
		self.sprite = None

	@property
	def enthalpy(self):
		"""Return enthalpy(aka H) for current state"""
		return self.state.enthalpy

	@property
	def entropy(self):
		"""Return entropy(aka S) for current state"""
		return self.state.entropy

	@property
	def state(self):
		"""Return current state"""
		return self.cml.get_state(self.current_state)
	@property
	def state_formula(self):
		return self.formula + "(%s)" % self.current_state

	def change_state(self, new_state):
		"""new_state: shortform of wanted state"""
		if not self.try_change_state(new_state):
			raise Exception("Tried to change: " + self.formula + " to non existing state:" + new_state)

	def try_change_state(self, new_state):
		"""new_state: shortform of wanted state"""
		pos = 0
		new_pos = -1
		for state in self.states:
			if state.short == new_state:
				new_pos = pos
			pos += 1
		if new_pos != -1:
			self.current_state = new_pos
			return True
		else:
			return False	
	
	def toAqueous(self):
		if self.try_change_state("aq"):
			return self.state.react()
		else:
			print "No Aq state exists for:", self.formula		

	def cml2Sprite(self, cmlfile):
		molecule = Cml.Molecule()
		molecule.parse(cmlfile)
		molecule.normalize_pos()
		self.sprite = PyGameUtil.createSurface(self.molecule_sprite_size(molecule))
		self.cml = molecule
		self.createBonds()
		for atom in molecule.atoms.values():
			atomSprite = self.createAtomSprite(atom.elementType, atom.formalCharge)
			self.sprite.blit(atomSprite, self.cartesian2pos(atom.pos))
		return self.sprite
		
					
	def createMoleculeSprite(self):
		self.sprite = PyGameUtil.createSurface(self.molecule_sprite_size(self.cml))
		self.createBonds()
		for atom in self.cml.atoms.values():
			atomSprite = self.createAtomSprite(atom.elementType, atom.formalCharge)
			self.sprite.blit(atomSprite, self.cartesian2pos(atom.pos))
		return self.sprite

	def cartesian2pos(self, pos):
		FACTOR = 42
		c_x, c_y = pos
		return (c_x * FACTOR,c_y * FACTOR)

	def cartesian2posBonds(self, pos):
		OFFSET = 16
		x, y = self.cartesian2pos(pos)
		return (x+OFFSET, y+OFFSET)

	def molecule_sprite_size(self, molecule):
		FACTOR = 42
		OFFSET = 32
		max_x, max_y, max_z = molecule.max_pos()
		return (max_x * FACTOR + OFFSET, max_y*FACTOR + OFFSET)
	
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

	def createAtomSprite(self,symbol, charge = None):
		if charge is None:
			charge = self.get_electric_charge(symbol)
			symbol = self.get_only_atom_symbol(symbol)
		if PyGameUtil.hasObject(symbol):
			return PyGameUtil.getObject(symbol+str(charge))
		atom =  PyGameUtil.loadImage("img/atom-" + symbol.lower() + ".png").copy()
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
		PyGameUtil.storeObject(symbol+str(charge), atom)
		return atom
	
	def createBonds(self):
		#pygame.draw.rect(self.sprite, pygame.color.THECOLORS["pink"], pygame.Rect(0,0, 1000, 1000))
		for bond in self.cml.bonds:
			#print bond.atomA.pos, "->", bond.atomB.pos
			posACenter = self.cartesian2posBonds(bond.atomA.pos)	
			posBCenter = self.cartesian2posBonds(bond.atomB.pos)
			posARight = (posACenter[0]+8, posACenter[1])	
			posBRight = (posBCenter[0]+8, posBCenter[1])
			#TODO add support for more than one bond
			pygame.draw.aaline(self.sprite, pygame.color.THECOLORS["black"],
			                 posACenter, posBCenter, 1)

	def get_only_atom_symbol(self, symbol):
		""" returns the atom symbol without any electric charge """
		return symbol.split("-")[0].split("+")[0]

class MoleculeSprite(pygame.sprite.Sprite):
	def __init__(self, molecule, space, pos=None):
		pygame.sprite.Sprite.__init__(self)
		self.molecule = molecule
		self.image_master = self.molecule.createMoleculeSprite()
		self.image = self.image_master
		self.rect = self.image.get_bounding_rect()
		self.active = False
		self.init_chipmunk(space)

		if pos == None:
			self.move((random.randint(10, 600), random.randint(10, 400)))
		else:
			self.move(pos)
	
	def cartesian2pymunk(self, pos):
		FACTOR = 42
		center_x, center_y = self.rect.center
		offset_x = -center_x + self.molecule.ATOM_SIZE/2
		offset_y = -center_y + self.molecule.ATOM_SIZE/2
		x, y = pos
		pymunk_pos = (offset_x + FACTOR*x,-(offset_y + FACTOR*y))
		return pymunk_pos

	def init_chipmunk(self,space):	
		body = pymunk.Body(10,moment = pymunk.inf)#pymunk.moment_for_circle(10, 0, 32))
		body.velocity_limit = 1000
		#shape = pymunk.Circle(body, 16)
		space.add(body)
		for atom in self.molecule.cml.atoms.values():
			circle = pymunk.Circle(body, 16, self.cartesian2pymunk(atom.pos))
			space.add(circle)
			self.shape = circle
			self.shape.elasticity = 0.95
			self.shape.collision_type = CollisionTypes.ELEMENT
			self.shape.sprite = self

		x = random.randrange(-10, 10)/10.0
		y = random.randrange(-10, 10)/10.0
		vec = Vec2d(x,y)
		force = 1500
		body.apply_impulse(force * vec)
	
	def move(self, pos):
		self.rect.center = pos
		self.shape.body.position = pymunk.pygame_util.from_pygame(pos, Config.current.screen)
		
	def update(self):
		self.rect.center =  pymunk.pygame_util.to_pygame(self.shape.body.position, Config.current.screen)
		#self.image = pygame.transform.rotate(self.image_master,math.degrees(self.shape.body.angle))
	        #self.rect = self.image.get_rect(center=self.rect.center)

