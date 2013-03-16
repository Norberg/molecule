import pygame

class Config:
	def __init__(self, DEBUG = False, level = 1):
		self.DEBUG = DEBUG
		self.level = level
		self.screenSize = (1024,768)
		self.screen = pygame.Surface(self.screenSize)

current = Config()
