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
	
	def init_chipmunk(self,space):	
		body = pymunk.Body(pymunk.inf, pymunk.inf)
		#shape = pymunk.Segment(body,(0,0), (128,0), 64)
		shape = pymunk.Poly.create_box(body, (128,128))
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

class Water_Beaker(pygame.sprite.Sprite):
	"""Water_Beaker"""
	def __init__(self, pos, space):
		pygame.sprite.Sprite.__init__(self)
		self.name = "Water Beaker"
		self.image = PyGameUtil.loadImage("img/water-beaker.png")
		self.rect = self.image.get_bounding_rect()
		self.rect.move_ip(pos)
		self.init_chipmunk(space)
		self.set_pos(pos)

	def init_chipmunk(self,space):	
		body = pymunk.Body(pymunk.inf, pymunk.inf)
		walls = [pymunk.Segment(body, (-144,-320), (-144, 200), 10), #left
		         pymunk.Segment(body, (-144,-320), (280, -320), 10), #bootom
		         pymunk.Segment(body, (277,-320), (277, 200), 10), #right
		         pymunk.Segment(body, (-144,200), (280, 200), 10) #top
                ]
		for wall in walls:
			wall.elasticity = 0.95
			wall.collision_type = 0
		space.add(walls)
		#shape = pymunk.Segment(body,(-134,-70), (267,-70), 480)
		shape = pymunk.Poly.create_box(body, (400,520), (66,-60))
		space.add(shape, body)
		self.shape = shape
		self.shape.collision_type = 2
		self.shape.sensor = True
		self.shape.effect = self
	
	def set_pos(self, pos):
		self.rect.center = pos
		self.shape.body.position = pymunk.pygame_util.from_pygame(pos, Config.current.screen)
