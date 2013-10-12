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
import glob
import pyglet
import pymunk
from molecule import Config
from molecule import CollisionTypes
from molecule import pyglet_util
from molecule import RenderingOrder
from libreact import Reaction
from libcml import Cml

class Fire(pyglet.sprite.Sprite):
	"""Fire"""
	def __init__(self, space, batch, pos, temp=1000):
		group = RenderingOrder.background
		img = pyglet_util.loadImage("img/fire/50 frames/fire1_ 50.png")
		pyglet.sprite.Sprite.__init__(self, img, batch=batch, group=group)
		self.name = "Fire"
		self.temp = temp
		self.current_frame = 0
		self.frames = 100
		self.animations = list()
		for img in sorted(glob.glob("img/fire/50 frames/*")):
			self.animations.append(pyglet_util.loadImage(img))
		self.image = self.animations[self.current_frame]
		self.init_chipmunk(space)
		self.set_pos(pos)
	
	def set_pos(self, pos):
		self.shape.body.position = pos
		x, y = self.shape.body.position
		self.x = x - self.width/2
		self.y = y - self.height/2
	
	def init_chipmunk(self,space):	
		body = pymunk.Body(pymunk.inf, pymunk.inf)
		shape = pymunk.Poly.create_box(body, (128,128))
		space.add(shape, body)
		self.shape = shape
		self.shape.collision_type = CollisionTypes.EFFECT
		self.shape.sensor = True
		self.shape.effect = self

	def update(self):
		self.current_frame += 1
		if self.current_frame >= self.frames:
			self.current_frame = 0

		self.image = self.animations[int(self.current_frame/2)]

	def react(self, element):
		pass

class Water_Beaker(pyglet.sprite.Sprite):
	"""Water_Beaker"""
	def __init__(self, space, batch, pos):
		img = pyglet_util.loadImage("img/water-beaker.png")
		group = RenderingOrder.background
		pyglet.sprite.Sprite.__init__(self, img, batch=batch, group=group)
		self.name = "Water Beaker"
		self.init_chipmunk(space)
		self.set_pos(pos)

	def init_chipmunk(self,space):	
		body = pymunk.Body(pymunk.inf, pymunk.inf)
		walls = [pymunk.Segment(body, (-144,-320), (-144, 200), 10), #left
		         pymunk.Segment(body, (-144,-320), (280, -320), 10), #bottom
		         pymunk.Segment(body, (277,-320), (277, 200), 10), #right
		         pymunk.Segment(body, (-144,200), (280, 200), 10) #top
                ]
		for wall in walls:
			wall.elasticity = 0.95
			wall.collision_type = CollisionTypes.WALL
			wall.layers = CollisionTypes.LAYER_WALL
		space.add(walls)
		shape = pymunk.Poly.create_box(body, (400,520), (66,-60))
		space.add(shape, body)
		self.shape = shape
		self.shape.collision_type = CollisionTypes.EFFECT
		self.shape.sensor = True
		self.shape.effect = self
	
	def set_pos(self, pos):
		OFFSET_X, OFFSET_Y = 60,-30
		self.shape.body.position = pos
		x, y = self.shape.body.position
		self.x = x - self.width/2 + OFFSET_X
		self.y = y - self.height/2 + OFFSET_Y

	def update(self):
		pass
	
	def react(self, molecule):
		ions = molecule.toAqueous()
		if ions != None and len(ions) > 0:
			print(molecule.formula, "-(Water)>", ions)
			cml = Cml.Reaction([molecule.formula],ions)
			reaction = Reaction.Reaction(cml,[molecule.state_formula])
			return reaction
		elif Config.current.DEBUG:
			print("Water beaker didnt react with:", molecule.formula)
			
