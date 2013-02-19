import pygame

def createSurface(x,y):
	return pygame.Surface((x,y), pygame.SRCALPHA)
def createSurface(x):
	return pygame.Surface((x,x), pygame.SRCALPHA)
