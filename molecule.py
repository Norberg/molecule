import time, os, random, inspect
 
import pygame
from pygame.locals import *

import levels
from Universe import Universe, Element

class Game:
	def __init__(self):
		pygame.init()
		self.screen = pygame.display.set_mode((640,480))
		pygame.display.set_caption('Molecule - A molecule builing puzzle game')
		self.clock = pygame.time.Clock()
		self.universe = Universe()

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

	def game_loop(self):
		for level in self.get_levels():
			result = self.run_level(level)
			if result == "victory":
				self.write_on_background("Congratulation, you finnished the level")
				self.wait(5)
				continue
			elif result == QUIT:
				return
			else:
				print "Unkown return code from level, quiting"
	
	def get_levels(self):
		for name, level in inspect.getmembers(levels):
			if inspect.isclass(level) and issubclass(level,levels.BaseLevel) and name != "BaseLevel":
				l = level()
				yield l

	def run_level(self, level):
		self.active = None
		self.write_on_background(level.description)
		self.elements = level.elements
		while 1:
			if self.event_loop() == QUIT:
				return QUIT
			if level.check_victory() == "victory":
				return "victory"

	def event_loop(self):
		self.clock.tick(60)
		for event in pygame.event.get():
			if event.type == QUIT:
				return QUIT
			elif event.type == KEYDOWN and event.key == K_ESCAPE:
				return QUIT
			elif event.type == MOUSEBUTTONDOWN:
				for element in reversed(self.elements.sprites()):
					if element.clicked():
						self.active = element
						break
			elif event.type is MOUSEBUTTONUP and self.active != None: 
				self.active.unclicked()
				self.active = None

		if self.active != None:
			for collition in pygame.sprite.spritecollide(self.active, self.elements, False):
				if collition != self.active:
					new_elements = self.active.react(collition)
					if new_elements != None:
						collition.kill()
						self.active.kill()
						self.active = None
						self.elements.add(new_elements)
					break	
		self.elements.update()
		self.screen.blit(self.background, (0, 0))
		#if active != None:
		#	pygame.draw.rect(screen, pygame.color.Color("black"), active.rect)
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
