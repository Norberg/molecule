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
import random
import math

import pyglet
from pymunk.vec2d import Vec2d
import pymunk

from molecule import pyglet_util
from molecule import CollisionTypes
from libcml import Cml
from libcml import CachedCml
from libreact import Reaction


class Molecule:
	def __init__(self, formula_with_state, space, batch, group, pos=None):
		self.space = space
		self.batch = batch
		self.group = group
		formula, state = Reaction.split_state(formula_with_state)
		self.formula = formula
		self.cml = CachedCml.getMolecule(formula)
		self.cml.normalize_pos()
		self.current_state = self.cml.get_state(state)
		if self.current_state is None:
			raise Exception("did not find state for:" + formula_with_state)
		self.create_atoms()
		self.vertexes = list()

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
		return self.current_state
	@property
	def state_formula(self):
		return self.formula + "(%s)" % self.current_state.short

	@property
	def draggable(self):
		return self.current_state.short != "aq"

	def change_state(self, new_state):
		"""new_state: shortform of wanted state"""
		if not self.try_change_state(new_state):
			raise Exception("Tried to change: " + self.formula + " to non existing state:" + new_state)

	def try_change_state(self, new_state):
		"""new_state: shortform of wanted state"""
		state = self.cml.get_state(new_state)
		if state is None:
			return False
		else:
			self.current_state = state
			return True	
	
	def toAqueous(self):
		if self.try_change_state("aq"):
			return self.state.ions
		else:
			print("No Aq state exists for:", self.formula)		
	
	def create_atoms(self):
		self.atoms = dict()
		for atom in self.cml.atoms.values():
			new = Atom(atom.elementType, atom.formalCharge,
			           self.space, self.batch, self.group, self)
			self.atoms[atom.id] = new
		self.create_bonds()

	def create_bonds(self):
		self.joints = list()
		for bond in self.cml.bonds:
			#bond.atomA.pos
			#bond.atomB.pos
			atomA = self.atoms[bond.atomA.id]
			atomB = self.atoms[bond.atomB.id]
			
			joint = pymunk.SlideJoint(atomA.body, atomB.body, (0,0), (0,0),
			                          10, 50)
			#joint.error_bias = math.pow(1.0-0.2, 30.0)
			self.joints.append(joint)
			self.space.add(joint) 


	def update(self):
		for atom in self.atoms.values():
			atom.update()
		
		for vertex in self.vertexes:
			vertex.delete()
		self.vertexes = list()

		for joint in self.joints:
			pv1 = joint.a.position #+ constraint.anchr1.rotated(constraint.a.angle)
			pv2 = joint.b.position #+ constraint.anchr2.rotated(constraint.b.angle)

			line = (pv1.x, pv1.y, pv2.x, pv2.y)
			color = (167,167,167)
			v = self.batch.add(2, pyglet.gl.GL_LINES, None,
			                   ('v2f', line),
			                   ('c3B', color * 2))
			self.vertexes.append(v)

	def delete(self):
		for vertex in self.vertexes:
			vertex.delete()
		self.vertexes = list()
		
		for atom in self.atoms.values():
			atom.delete()
		self.atoms = dict()

		for joint in self.joints:
			self.space.remove(joint)
		self.joints = list()
		

class Atom(pyglet.sprite.Sprite):
	def __init__(self, symbol, charge, space, batch, group, molecule, pos=None):
		#TODO create a copy..
		img = pyglet_util.loadImage("img/atom-" + symbol.lower() + ".png")
		pyglet.sprite.Sprite.__init__(self, img, batch=batch, group=group)
		self.molecule = molecule
		self.space = space
		self.active = False
		self.init_chipmunk()

		if pos == None:
			self.move((random.randint(10, 600), random.randint(10, 400)))
		else:
			self.move(pos)
	
	def init_chipmunk(self):	
		body = pymunk.Body(10,moment = pymunk.inf)#pymunk.moment_for_circle(10, 0, 32))
		body.velocity_limit = 1000
		shape = pymunk.Circle(body, 16)
		shape.elasticity = 0.95
		shape.collision_type = CollisionTypes.ELEMENT
		shape.molecule = self.molecule
		self.space.add(body, shape)

		x = random.randrange(-10, 10)/10.0
		y = random.randrange(-10, 10)/10.0
		vec = Vec2d(x,y)
		force = 1500
		body.apply_impulse(force * vec)
		self.body = body
		self.shape = shape

	@property
	def affecty_by_gravity(self):
		return False
		return self.molecule.current_state.short == "s"

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
	
	def get_only_atom_symbol(self, symbol):
		""" returns the atom symbol without any electric charge """
		return symbol.split("-")[0].split("+")[0]
	
	def cartesian2pymunk(self, pos):
		FACTOR = 42
		center_x, center_y = self.rect.center
		offset_x = -center_x + self.molecule.ATOM_SIZE/2
		offset_y = -center_y + self.molecule.ATOM_SIZE/2
		x, y = pos
		pymunk_pos = (offset_x + FACTOR*x,-(offset_y + FACTOR*y))
		return pymunk_pos

	def move(self, pos):
		self.body.position = pos
		
	def update(self):
		x, y = self.body.position
		self.x = x - self.width/2
		self.y = y - self.height/2
		if self.affecty_by_gravity:
			self.body.velocity_func = self.gravity_func
		else:
			self.body.velocity_func = pymunk.Body.update_velocity

	def gravity_func(self, body, gravity, damping, dt):
		gravity = (0.0,-500.0)
		return pymunk.Body.update_velocity(body, gravity, damping, dt)

	def delete(self):
		self.space.remove(self.shape)
		self.space.remove(self.body)
		super(Atom, self).delete()
