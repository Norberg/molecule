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
import getopt
import sys
import time
import os
import random
import inspect
import math
 
import pygame
from pygame.locals import *
import pymunk

from pymunk import pygame_util

from molecule import Universe
from molecule import Config
from molecule import CollisionTypes	
from molecule.Levels import Levels

class Game:
	def __init__(self, gui = True):
		self.last_collision = 0
		self.handle_cmd_options()
		if gui:
			self.init_pygame()
		self.space = None
		Universe.createUniverse()
		self.mouse_body = pymunk.Body()	
		self.mouse_spring = None
		self.DEBUG_GRAPHICS = False
	
	def init_pygame(self):	
		pygame.init()
		self.screen = pygame.display.set_mode(Config.current.screenSize)
		pygame.display.set_caption('Molecule - A molecule builing puzzle game')
		self.clock = pygame.time.Clock()

	def write_on_background(self, text):
		self.background = pygame.Surface(self.screen.get_size())
		self.background = self.background.convert()
		self.background.fill((250, 250, 250))
		font = pygame.font.Font(None, 36)
		text = font.render(text, 1, (10, 10, 10))
		textpos = text.get_rect(centerx=self.background.get_width()/2)
		self.background.blit(text, textpos)

		self.screen.blit(self.background, (0, 0))
		pygame.display.flip()

	def wait(self, seconds):
		"""pause game for a few seconds"""	
		end = time.time() + seconds
		while time.time() < end:
			self.event_loop()
	
	def handle_cmd_options(self):
		try:
			opts, args = getopt.getopt(sys.argv[1:], "hld", ["help", "level=", "debug",])
		except getopt.GetoptError as err:
			print(str(err))
			self.cmd_help()
			sys.exit(2)
		for o,a in opts:
			if o in ("-h", "--help"):
				self.cmd_help()
				sys.exit()
			elif o in ("-l", "--level"):
				Config.current.level = int(a)
			elif o in ("-d", "--debug"):
				Config.current.DEBUG = True
			
				
	def cmd_help(self):
		print("Molecule - a chemical reaction puzzle game")
		print("-h --help print this help")	
		print("--level=LEVEL choose what level to start on")	
		print("-d --debug print debug messages")
		print("During gameplay:")
		print("ESC - close game")
		print("r - reset current level")	
		print("d - switch Graphic debug on/off")	
		print("s - skip level")	

	
	def game_loop(self):
		levels = Levels("data/levels")
		levels.current_level = Config.current.level -2 
		for level in levels.level_iter():
			while 1:
				result = self.run_level(level)
				if result == "victory":
					self.write_on_background("Congratulation, you finished the level")
					self.wait(2)
					break
				elif result == "SKIP_LEVEL":
					self.write_on_background("Skipped level, Cheater!")
					self.wait(1)
					break
				elif result == "RESET_LEVEL":
					level.reset()
					continue	
				elif result == QUIT:
					return
				else:
					print("Unkown return code from level, quiting")
	
	def run_level(self, level):
		self.active = None
		self.write_on_background(level.cml.objective)
		self.elements = level.elements
		self.areas = level.areas
		self.space = level.space
		self.mouse_spring = None
		self.space.add_collision_handler(CollisionTypes.ELEMENT, CollisionTypes.ELEMENT, post_solve=self.element_collision)
		self.space.add_collision_handler(CollisionTypes.ELEMENT, CollisionTypes.EFFECT, begin=self.effect_reaction)
		while 1:
			event = self.event_loop()
			if event != None:
				return event
			if level.check_victory():
				return "victory"

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
		molecule = a.sprite.molecule
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
		position = pymunk.pygame_util.to_pygame(position, Config.current.screen)
		self.elements.add(Universe.create_elements(self.space, reaction.products, position))

	def destroy_elements(self, elements_to_destroy, collisions):
		""" Destroy a list of elements from a dict of collisions"""
		elements = list(elements_to_destroy)
		removed_bodies = list()
		for collision in collisions:
			if collision["shape"].collision_type == CollisionTypes.ELEMENT:
				shape = collision["shape"]
				sprite = shape.sprite
				formula = sprite.molecule.state_formula
				if formula in elements and \
				   id(shape.body) not in removed_bodies:
					removed_bodies.append(id(shape.body))
					elements.remove(formula)
					for s in shape.body.shapes:
						self.space.remove(s)
					self.space.remove(shape.body)
					sprite.kill()
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
				if shape.sprite not in molecules:
					molecules.append(shape.sprite)
					yield shape.sprite.molecule.state_formula

	def update_mouse_pos(self):
		pygame_pos = pygame.mouse.get_pos()		
		mouse_pos = pymunk.pygame_util.from_pygame(pygame_pos, Config.current.screen)
		self.mouse_body.position = mouse_pos
		return mouse_pos

	def event_loop(self):
		#self.space.step(1/60.0)
		self.space.step(1/60.0)
		self.clock.tick(60)
		self.update_mouse_pos()
		for event in pygame.event.get():
			res = self.handle_event(event)
			if res is not None:
				return res
		self.screen.blit(self.background, (0, 0))
		self.update_and_draw(self.areas, self.elements)


	def handle_event(self, event):
		if event.type == QUIT:
			return QUIT
		elif event.type == KEYDOWN and event.key == K_ESCAPE:
			return QUIT
		elif event.type == KEYDOWN and event.key == K_r:
			return "RESET_LEVEL"
		elif event.type == KEYDOWN and event.key == K_d:
			self.DEBUG_GRAPHICS = not self.DEBUG_GRAPHICS
		elif event.type == KEYDOWN and event.key == K_s:
			return "SKIP_LEVEL"
		elif event.type == MOUSEBUTTONDOWN:
			self.handle_mouse_button_down()	
		elif event.type is MOUSEBUTTONUP: 
			self.handle_mouse_button_up()

	def handle_mouse_button_down(self):
		if self.mouse_spring != None:
			raise Exception("mouse_spring already existing")
		clicked = self.space.nearest_point_query_nearest(self.update_mouse_pos(), 16)
		if clicked != None and \
		   clicked["shape"].collision_type == CollisionTypes.ELEMENT and \
		   clicked["shape"].sprite.molecule.draggable:
			clicked = clicked["shape"]
			rest_length = self.mouse_body.position.get_distance(clicked.body.position)
			self.mouse_spring = pymunk.PivotJoint(self.mouse_body, clicked.body, (0,0), (0,0))
			self.mouse_spring.error_bias = math.pow(1.0-0.2, 30.0)
			clicked.body.mass /= 50
			self.space.add(self.mouse_spring) 

	def handle_mouse_button_up(self):
		if self.mouse_spring != None:
			self.mouse_spring.b.mass *= 50
			self.mouse_spring.b.velocity = (0,0)
			self.space.remove(self.mouse_spring)
			self.mouse_spring = None

	def update_and_draw(self, *spriteGroups):
		dirty_rects = list()
				
		for spriteGroup in spriteGroups:
			spriteGroup.update()
			dirty_rect = spriteGroup.draw(self.screen)
			try:	
				dirty_rects += dirty_rect
			except:
				pass
		if self.DEBUG_GRAPHICS:
			pygame_util.draw(self.screen, self.space)
			pygame.display.update()
		else:	
			pygame.display.update(dirty_rects)
