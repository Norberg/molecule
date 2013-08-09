import pygame

def createSurface(x,y):
	return pygame.Surface((int(x),int(y)), pygame.SRCALPHA)
def createSurface(pos):
	print pos
	if type(pos) == tuple:
		x = pos[0]
		y = pos[1]
	else:
		x = pos
		y = pos	

	return pygame.Surface((int(x),int(y)), pygame.SRCALPHA)

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
