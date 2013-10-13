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
import sys
import time
import os
import random
import inspect
import math
 
import pymunk
from pymunk import pyglet_util
import pyglet
from pyglet.window import mouse
from pyglet import gl

from molecule import Universe
from molecule import Config
from molecule import CollisionTypes	
from molecule.Levels import Levels


class Game(pyglet.window.Window):
	def __init__(self):
		w, h = Config.current.screenSize
		config = pyglet.gl.Config(sample_buffers=1, samples=4, double_buffer=True)
		super(Game, self).__init__(caption="Molecule", config=config,
		                           vsync=True, width=w, height=h)
		self.init_pyglet()
		self.init_pymunk()
		Universe.createUniverse()
		self.DEBUG_GRAPHICS = False
		self.start()

	def start(self):
		self.write_on_background("Welcome to Molecule")
		pyglet.gl.glClearColor(250/256.0, 250/256.0, 250/256.0, 0)
		self.fps_display = pyglet.clock.ClockDisplay()
		self.levels = Levels("data/levels", Config.current.level)
		level = self.levels.next_level()
		self.run_level(0, level)	
		pyglet.clock.schedule_interval(self.update, 1/100.0)
	
	def init_pymunk(self):
		self.last_collision = 0
		self.space = None
		self.mouse_body = pymunk.Body()	
		self.mouse_spring = None

	def init_pyglet(self):
		gl.glLineWidth(4)
		gl.glHint(gl.GL_LINE_SMOOTH_HINT, gl.GL_NICEST)	
	
	def write_on_background(self, text):
		self.label = pyglet.text.Label(text,
		                               font_name = 'Times New Roman',
		                               font_size = 36,
		                               color = (0,0,0,255),
		                               x = self.width//2, y = self.height-100,
		                               anchor_x = 'center', anchor_y = 'center')
		
	def on_draw(self):
		self.clear()
		self.label.draw()
		self.level.update()
		self.batch.draw()
		if self.DEBUG_GRAPHICS:
			pymunk.pyglet_util.draw(self.space)
		self.fps_display.draw()
	
	def close(self, dt=None):
		super(Game, self).close()
	
	def run_level(self, dt, level):
		if level is None:
			self.write_on_background("Victory!, You have finished the game!")
			pyglet.clock.schedule_once(self.close, 3)
			return
		self.active = None
		self.write_on_background(level.cml.objective)
		self.batch = level.batch
		self.level = level
		self.space = level.space
		self.victory = False
		self.mouse_spring = None
		self.space.add_collision_handler(CollisionTypes.ELEMENT, CollisionTypes.ELEMENT, post_solve=self.element_collision)
		self.space.add_collision_handler(CollisionTypes.ELEMENT, CollisionTypes.EFFECT, begin=self.effect_reaction)

	def element_collision(self, space, arbiter):
		""" Called if two elements collides"""
		a,b = arbiter.shapes
		reacting_areas = list(self.get_affecting_areas(a.body.position))
		collisions = space.nearest_point_query(a.body.position, 100)
		reacting_elements = list(self.get_element_symbols(collisions))
		reaction = Universe.universe.react(reacting_elements, reacting_areas)
		if reaction != None:
			key = 1 # use 1 as key so only one callback per iteration can trigger 
			space.add_post_step_callback(self.perform_reaction, key, reaction, collisions, a.body.position)

	def effect_reaction(self, space, arbiter):
		""" Called if an element touches a effect """
		a,b = arbiter.shapes
		molecule = a.molecule
		effect = b.effect
		reaction = effect.react(molecule)
		collisions = [{"shape" : a}]
		if reaction != None:
			key = 1 # use 1 as key so only one callback per iteration can trigger 
			space.add_post_step_callback(self.perform_reaction, key, reaction, collisions, b.body.position)	
		return False

	def perform_reaction(self, key, reaction, collisions, position):
		""" Perform a reaction"""
		self.destroy_elements(reaction.reactants, collisions)
		self.level.create_elements(reaction.products, position)
		self.victory = self.level.check_victory()

	def destroy_elements(self, elements_to_destroy, collisions):
		""" Destroy a list of elements from a dict of collisions"""
		elements = list(elements_to_destroy)
		removed_bodies = list()
		for collision in collisions:
			if collision["shape"].collision_type == CollisionTypes.ELEMENT:
				shape = collision["shape"]
				molecule = shape.molecule
				formula = molecule.state_formula
				if formula in elements and \
				   id(shape.body) not in removed_bodies:
					removed_bodies.append(id(shape.body))
					elements.remove(formula)
					molecule.delete()
		if len(elements) != 0:
			print("not all elements was removed..")
			print("elements_to_destroy:", elements_to_destroy)
			print("collisions:", collisions)

	def get_affecting_areas(self, position):
		"""Return all areas that have a affect on position"""
		shapes = self.space.point_query(position)
		for shape in shapes:
			if shape.collision_type == CollisionTypes.EFFECT:
				yield shape.effect

	def get_element_symbols(self, collisions):
		"""Take a collison dict and return a list of symbols for every unique molecule"""
		molecules = list()
		for collision in collisions:
			shape = collision["shape"]
			if shape.collision_type == CollisionTypes.ELEMENT:
				if shape.molecule not in molecules:
					molecules.append(shape.molecule)
					yield shape.molecule.state_formula

	def limit_pos_to_screen(self, x, y):
		x = max(0,x)
		y = max(0,y)
		w, h = Config.current.screenSize
		x = min(w,x)
		y = min(h,y)
		return x,y 

	def on_mouse_press(self, x, y, button, modifiers):
		self.handle_mouse_button_down(x, y)

	def on_mouse_release(self, x, y, button, modifiers):
		if self.mouse_spring != None:
			self.mouse_spring.b.mass *= 50
			self.mouse_spring.b.velocity = (0,0)
			self.mouse_spring.b.molecule.set_dragging(False)
			self.space.remove(self.mouse_spring)
			self.mouse_spring = None
	
	def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
		x,y = self.limit_pos_to_screen(x,y)
		self.mouse_body.position = (x, y)

	def on_key_press(self, symbol, modifiers):
		if symbol == pyglet.window.key.M:
			print("dumping memory..")
			from meliae import scanner
			scanner.dump_all_objects("memory.dump")
		elif symbol == pyglet.window.key.ESCAPE:
			self.close()
		elif symbol == pyglet.window.key.S:	
			self.write_on_background("Skipping level, Cheater!")
			level = self.levels.next_level()
			pyglet.clock.schedule_once(self.run_level, 1, level)
			self.victory = False
		elif symbol == pyglet.window.key.R:
			print("reseting..")	
			self.level.reset()
			self.run_level(0, self.level)
		elif symbol == pyglet.window.key.D:	
			self.DEBUG_GRAPHICS = not self.DEBUG_GRAPHICS

	def update(self, dt):
		self.space.step(1/60.0)
		if self.victory:
			self.write_on_background("Congratulation, you finished the level")
			level = self.levels.next_level()
			pyglet.clock.schedule_once(self.run_level, 3, level)
			self.victory = False

	def handle_mouse_button_down(self, x, y):
		if self.mouse_spring != None:
			raise Exception("mouse_spring already existing")
		self.mouse_body.position = (x, y)
		clicked = self.space.nearest_point_query_nearest((x,y), 16)
		if (clicked != None and 
		    clicked["shape"].collision_type == CollisionTypes.ELEMENT and
		    clicked["shape"].molecule.draggable):
			clicked = clicked["shape"]
			clicked.molecule.set_dragging(True)
			rest_length = self.mouse_body.position.get_distance(clicked.body.position)
			self.mouse_spring = pymunk.PivotJoint(self.mouse_body, clicked.body, (0,0), (0,0))
			self.mouse_spring.error_bias = math.pow(1.0-0.2, 30.0)
			clicked.body.mass /= 50
			self.space.add(self.mouse_spring) 
