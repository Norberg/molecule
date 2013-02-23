import glob
import pygame
import PyGameUtil

class Fire(pygame.sprite.Sprite):
	"""Fire"""
	def __init__(self, pos):
		pygame.sprite.Sprite.__init__(self)
		self.name = "Fire"
		self.current_frame = 0
		self.frames = 50
		self.animations = list()
		for img in sorted(glob.glob("img/fire/50 frames/*")):
			self.animations.append(PyGameUtil.loadImage(img))
		self.image = self.animations[self.current_frame]
		self.rect = self.image.get_bounding_rect()
		self.rect.move_ip(pos)
				

	def update(self):
		self.current_frame += 1
		if self.current_frame >= self.frames:
			self.current_frame = 0

		self.image = self.animations[self.current_frame]
