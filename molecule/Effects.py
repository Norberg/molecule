import glob
import pygame
import pymunk
import PyGameUtil
import molecule.Config as Config

class Fire(pygame.sprite.Sprite):
	"""Fire"""
	def __init__(self, pos, space, temp=1000):
		pygame.sprite.Sprite.__init__(self)
		self.name = "Fire"
		self.temp = temp
		self.current_frame = 0
		self.frames = 50
		self.animations = list()
		for img in sorted(glob.glob("img/fire/50 frames/*")):
			self.animations.append(PyGameUtil.loadImage(img))
		self.image = self.animations[self.current_frame]
		self.rect = self.image.get_bounding_rect()
		self.init_chipmunk(space)
		self.set_pos(pos)
	
	def set_pos(self, pos):
		self.rect.center = pos
		self.shape.body.position = pymunk.pygame_util.from_pygame(pos, Config.current.screen)
		print  self.shape.body.position
	
	def init_chipmunk(self,space):	
		body = pymunk.Body(pymunk.inf, pymunk.inf)
		shape = pymunk.Segment(body,(0,0), (128,0), 128)
		space.add(shape, body)
		self.shape = shape
		self.shape.collision_type = 2
		self.shape.sensor = True
		self.shape.effect = self

	def update(self):
		self.current_frame += 1
		if self.current_frame >= self.frames:
			self.current_frame = 0

		self.image = self.animations[self.current_frame]
