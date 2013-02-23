import getopt, sys, time, os, random, inspect
 
import pygame
from pygame.locals import *

import levels
from Universe import Universe, Element, Fire

class Config:
	__config = dict() #Share config by all instance of this class
	def ___init__(self):
		self.__dict = self.__config

	def __init__(self, DEBUG = False, level = 1):
		self.__dict = self.__config
		self.DEBUG = DEBUG
		self.level = level
		

class Game:
	def __init__(self):
		self.last_collision = 0
		self.config = Config()
		self.handle_cmd_options()	
		self.init_pygame()
		self.universe = Universe()
		self.universe.config = self.config
		
	def init_pygame(self):	
		pygame.init()
		self.screen = pygame.display.set_mode((640,480))
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
				self.config.level = int(a)
			elif o in ("-d", "--debug"):
				self.config.DEBUG = True
			
				
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
		for name, level in inspect.getmembers(levels):
			if inspect.isclass(level) and issubclass(level,levels.BaseLevel) \
			   and name != "BaseLevel" and int(name.split("_")[1]) >= self.config.level:
				l = level()
				yield l

	def run_level(self, level):
		self.active = None
		self.write_on_background(level.description)
		self.elements = level.elements
		self.areas = level.areas
		while 1:
			event = self.event_loop()
			if event != None:
				return event
			if level.check_victory() == "victory":
				return "victory"

	"""Return a generator with all colliding elements, set to_match to sprite if not mathing against active sprite"""
	def get_colliding_elements(self, to_match = None):
		if self.active != None and to_match == None:
			for collition in pygame.sprite.spritecollide(self.active, self.elements, False):
				yield collition
		elif to_match != None:
			for collition in pygame.sprite.spritecollide(to_match, self.elements, False):
				yield collition
			

	"""Return all areas that collidies with active element"""
	def get_colliding_areas(self):
		if self.active != None:
			for collition in pygame.sprite.spritecollide(self.active, self.areas, False):
				yield collition

	def get_colliding_areas_name(self, areas):
		for area in areas:
			yield area.name

	"""Take a element generator and return a symbol list"""
	def get_element_symbols(self, elements):
		for element in elements:
			yield element.molecule.formula

	def event_loop(self):
		self.clock.tick(30)
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
		
		colliding_areas = list(self.get_colliding_areas())
		if len(colliding_areas) > 0:
			reacting_elements = list(self.get_colliding_elements(to_match = colliding_areas[0]))
		else:		
			reacting_elements = list(self.get_colliding_elements())
		if self.last_collision != len(reacting_elements) + 10000*len(colliding_areas):
			self.last_collision = len(reacting_elements) + 10000*len(colliding_areas)
			reaction = self.universe.react(list(self.get_element_symbols(reacting_elements)),
			                               list(self.get_colliding_areas_name(colliding_areas)))
			if reaction != None:
				self.active = None
				for element in reacting_elements:
					#FIXME eg 2 H are in a reaction both will be removed even if only one is consumed
					if element.molecule.formula in reaction.consumed: 
						element.kill()
				self.elements.add(self.universe.create_elements(reaction.result, pos = pygame.mouse.get_pos()))
				
	
		self.elements.update()
		self.areas.update()
		self.screen.blit(self.background, (0, 0))
		#if active != None:
		#	pygame.draw.rect(screen, pygame.color.Color("black"), active.rect)
		self.areas.draw(self.screen)
		self.elements.draw(self.screen)
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
