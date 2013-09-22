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

import pyglet
from pymunk.vec2d import Vec2d
import pymunk

from molecule import pyglet_util
from molecule import CollisionTypes

class Atom(pyglet.sprite.Sprite):
	def __init__(self, symbol, space, batch, group, pos=None):
		charge = self.get_electric_charge(symbol)
		symbol = self.get_only_atom_symbol(symbol)
		#TODO create a copy..
		img = pyglet_util.loadImage("img/atom-" + symbol.lower() + ".png")
		pyglet.sprite.Sprite.__init__(self, img, batch=batch, group=group)
		self.active = False
		self.init_chipmunk(space)

		if pos == None:
			self.move((random.randint(10, 600), random.randint(10, 400)))
		else:
			self.move(pos)
	
	def init_chipmunk(self,space):	
		body = pymunk.Body(10,moment = pymunk.inf)#pymunk.moment_for_circle(10, 0, 32))
		body.velocity_limit = 1000
		shape = pymunk.Circle(body, 16)
		shape.elasticity = 0.95
		shape.collision_type = CollisionTypes.ELEMENT
		space.add(body, shape)

		x = random.randrange(-10, 10)/10.0
		y = random.randrange(-10, 10)/10.0
		vec = Vec2d(x,y)
		force = 1500
		body.apply_impulse(force * vec)
		self.body = body

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
