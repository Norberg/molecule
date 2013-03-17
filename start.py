import getopt, sys, time, os, random, inspect
 
import pygame
from pygame.locals import *
import pymunk

from pymunk.pygame_util import draw_space

import molecule.levels
import molecule.Universe as Universe
import molecule.Config as Config
		

class Game:
	def __init__(self):
		self.last_collision = 0
		self.handle_cmd_options()	
		self.init_pygame()
		self.space = None
		Universe.createUniverse()
		self.count = 0	
	
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

	"""pause game for a few seconds"""	
	def wait(self, seconds):
		end = time.time() + seconds
		while time.time() < end:
			self.event_loop()
	
	def handle_cmd_options(self):
		try:
			opts, args = getopt.getopt(sys.argv[1:], "hld", ["help", "level=", "debug",])
		except getopt.GetoptError as err:
   			print str(err)
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
		print "Molecule - a Molecule reaction puzzle game by Simon Norberg"
		print "-h --help print this help"	
		print "--level=LEVEL choose what level to start on"	
		print "-d --debug print debug messages"
		print "During gameplay:"
		print "ESC - close game"
		print "r - reset current level"	

	
	def game_loop(self):
		for level in self.get_levels():
			while 1:
				result = self.run_level(level)
				if result == "victory":
					self.write_on_background("Congratulation, you finnished the level")
					self.wait(2)
					break
				elif result == "RESET_LEVEL":
					level.__init__()
					continue	
				elif result == QUIT:
					return
				else:
					print "Unkown return code from level, quiting"
	
	def get_levels(self):
		for name, level in inspect.getmembers(molecule.levels):
			if inspect.isclass(level) and issubclass(level,molecule.levels.BaseLevel) \
			   and name != "BaseLevel" and int(name.split("_")[1]) >= Config.current.level:
				l = level()
				yield l

	def run_level(self, level):
		self.active = None
		self.write_on_background(level.description)
		self.elements = level.elements
		self.areas = level.areas
		self.space = level.space
		self.space.add_collision_handler(1, 1, post_solve=self.element_collision)
		while 1:
			event = self.event_loop()
			if event != None:
				return event
			if level.check_victory() == "victory":
				return "victory"

	def element_collision(self, space, arbiter):
		a,b = arbiter.shapes
		reacting_areas = list(self.get_affecting_areas(a.body.position))
		collisions = space.nearest_point_query(a.body.position, 30)
		reacting_elements = list(self.get_element_symbols(collisions))
		reaction = Universe.universe.react(reacting_elements, reacting_areas)
		if reaction != None:
			space.add_post_step_callback(self.perform_reaction, reaction, collisions, a.body.position)

	def perform_reaction(self, reaction, collisions, position):
		self.destroy_elements(reaction.reactants, collisions)
		position = pymunk.pygame_util.to_pygame(position, Config.current.screen)
		self.elements.add(Universe.universe.create_elements(self.space, reaction.products, position))

	def destroy_elements(self, elements_to_destroy, collisions):
		""" Destroy a list of elements from a dict of collisions"""
		elements = list(elements_to_destroy)
		for collision in collisions:
			if collision["shape"].collision_type == 1:
				shape = collision["shape"]
				sprite = shape.sprite
				formula = sprite.molecule.formula
				if formula in elements:
					elements.remove(formula)
					self.space.remove(shape)
					sprite.kill()


	def get_affecting_areas(self, position):
		"""Return all areas that have a affect on position"""
		shapes = self.space.point_query(position)
		for shape in shapes:
			if shape.collision_type == 2:
				yield shape.effect

	def get_element_symbols(self, collisions):
		"""Take a collison dict and return a list of symbols"""
		for collision in collisions:
			if collision["shape"].collision_type == 1:
				yield collision["shape"].sprite.molecule.formula

	def update_active(self):
		if self.active != None:
			self.active.update()

	def event_loop(self):
		self.space.step(1/60.0)
		self.space.step(1/60.0)
		self.clock.tick(30)
		self.update_active()
		for event in pygame.event.get():
			if event.type == QUIT:
				return QUIT
			elif event.type == KEYDOWN and event.key == K_ESCAPE:
				return QUIT
			elif event.type == KEYDOWN and event.key == K_r:
				return "RESET_LEVEL"
			elif event.type == MOUSEBUTTONDOWN:
				for element in reversed(self.elements.sprites()):
					if element.clicked():
						self.active = element
						break
			elif event.type is MOUSEBUTTONUP and self.active != None: 
				self.active.unclicked()
				self.active = None
		"""	
		colliding_areas = list(self.get_colliding_areas())
		if len(colliding_areas) > 0:
			reacting_elements = list(self.get_colliding_elements(to_match = colliding_areas[0]))
		else:		
			reacting_elements = list(self.get_colliding_elements())
		if self.last_collision != len(reacting_elements) + 10000*len(colliding_areas):
			self.last_collision = len(reacting_elements) + 10000*len(colliding_areas)
			reaction = Universe.universe.react(list(self.get_element_symbols(reacting_elements)),
			                                   colliding_areas)
			if reaction != None:
				self.active = None
				for element in reacting_elements:
					#FIXME eg 2 H are in a reaction both will be removed even if only one is consumed
					if element.molecule.formula in reaction.reactants:
						self.space.remove(element.shape) 
						element.kill()
				self.elements.add(Universe.universe.create_elements(self.space, reaction.products, pos = pygame.mouse.get_pos()))
		"""	
		self.elements.update()
		self.areas.update()
		self.screen.blit(self.background, (0, 0))
		#if active != None:
		#	pygame.draw.rect(screen, pygame.color.Color("black"), active.rect)
		self.areas.draw(self.screen)
		self.elements.draw(self.screen)
		#draw_space(self.screen, self.space)	
		pygame.display.flip()
			

	

def main():
	game = Game()
	game.game_loop()

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		pass
	from guppy import hpy
	h = hpy()
	print h.heap()
