import pygame

def createSurface(x,y):
	return pygame.Surface((x,y), pygame.SRCALPHA)
def createSurface(x):
	return pygame.Surface((x,x), pygame.SRCALPHA)

__img_cache = dict()
def loadImage(src):
	if __img_cache.has_key(src):
		return __img_cache[src]
	global __img_cache	
	img = pygame.image.load(src).convert_alpha()
	__img_cache[src] = img
	return __img_cache[src]

__object_cache = dict()

def storeObject(key, obj):
	global __object_cache
	__object_cache[key] = obj

def getObject(key):
	return __object_cache[key]

def hasObject(key):
	return __object_cache.has_key(key)
