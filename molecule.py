import os, pygame,random
from pygame.locals import *


class Universe:
	"""Universe contains all fundamental particles and laws needed to get the universe to spin"""
	def __init__(self):
		self.moelcules = dict()
		self.link_right = pygame.image.load("img/link-right.png")
		self.link_left = pygame.image.load("img/link-left.png")
		self.link_top = pygame.image.load("img/link-top.png")
		self.link_bottom = pygame.image.load("img/link-bottom.png")

	def reaction_table(self, a, b):
		if a == 'O':
			if b == 'H':
				return "OH"
			elif b == 'O':
				return "OO"
			elif b == 'H2':
				return "H2O"
		elif a == 'H':
			if b == 'H':
				return "H2"
			elif b == 'OH':
				return "H2O"

	def molecule_table(self, molecule):
		layout = dict()
		if molecule == "OH":
			layout[(1,1)] = 'O'	
			layout[(2,1)] = 'H'
		elif molecule == "H2":
			layout[(1,1)] = 'H'	
			layout[(2,1)] = 'H'
		elif molecule == "H2O":
			layout[(1,1)] = 'H'	
			layout[(2,1)] = 'O'
			layout[(3,1)] = 'H'	
		else:
			print "No layout found for:", molecule
			return None
		return layout

	def create_atom(self, symbol, copy=True):
		if not self.moelcules.has_key(symbol):
			self.moelcules[symbol] =  pygame.image.load("img/atom-" + symbol.lower() + ".png")
		if copy:
			return self.moelcules[symbol].copy()
		else:
			return self.moelcules[symbol]
	
	def pos2cord(self, pos):
		x, y = pos
		return (32*(x-1), 32*(y-1))

	def pos2cord_link(self, pos, direction):
		x, y = self.pos2cord(pos)
		if direction == "top":
			return (x+1, y-3)
		elif direction == "bottom":
			return (x+1, y+2)
		elif direction == "left":
			return (x-2, y)
		elif direction == "right":
			return (x+3, y)
				
	def create_links(self, layout):
		links = pygame.Surface((160,160), 0, self.create_atom('O', copy=False))
		for pos in layout.keys():
				x,y = pos
				if layout.has_key((x, y-1)): #Top
					link_pos = self.pos2cord_link(pos, "top")
					links.blit(self.link_top, link_pos)
				elif layout.has_key((x, y+1)): #Bottom
					link_pos = self.pos2cord_link(pos, "bottom")
					links.blit(self.link_bottom, link_pos)
				elif layout.has_key((x-1, y)): #Left
					link_pos = self.pos2cord_link(pos, "left")
					links.blit(self.link_left, link_pos)
				elif layout.has_key((x+1, y)): #Right
					link_pos = self.pos2cord_link(pos, "right")
					links.blit(self.link_right, link_pos)
		return links


	def create_molecule(self, symbol):
		layout = self.molecule_table(symbol)
		if layout != None:
			molecule = pygame.Surface((160,160), 0, self.create_atom('O', copy=False))
			for pos in layout.keys():
				symbol = layout[pos]
				atom = self.create_atom(symbol, copy=False)
				molecule.blit(atom, self.pos2cord(pos))
			links = self.create_links(layout)
			molecule.blit(links, (0,0))
			return molecule
			
universe = Universe()

class Atom(pygame.sprite.Sprite):
	"""Atom - The universal buildning block"""
	def __init__(self, symbol):
		pygame.sprite.Sprite.__init__(self)
		self.symbol = symbol
		self.image = pygame.image.load("img/atom-" + self.symbol.lower() + ".png")
		self.rect = self.image.get_rect()	
		self.rect.move_ip(random.randint(10, 600), random.randint(10, 400))
		self.active = False
	

	def update(self):
		if self.active:	
			pos = pygame.mouse.get_pos()
			self.rect.midtop = pos

	def clicked(self):
		if self.rect.collidepoint(pygame.mouse.get_pos()):
			self.active = True
			return True
		else:
			return False

	def unclicked(self):
		if self.active:
			self.active = False
			return True
		else:
			return False

	def react(self, other):
		reaction = universe.reaction_table(self.symbol, other.symbol)
		if reaction == None:
			reaction = universe.reaction_table(other.symbol, self.symbol)
		if reaction != None:
			self.transform(reaction)
			print "Created:", reaction
			return True
		return False

	def transform(self, new_symbol):
		image = universe.create_molecule(new_symbol)
		if image != None:
			self.image = image
			self.symbol = new_symbol
			self.rect = self.image.get_rect()
			

def main():
	pygame.init()
	screen = pygame.display.set_mode((640,480))
	pygame.display.set_caption('Molecule - A molecule builing puzzle game')

	background = pygame.Surface(screen.get_size())
	background = background.convert()
	background.fill((250, 250, 250))

	if pygame.font:
		font = pygame.font.Font(None, 36)
		text = font.render("Create a water molecule", 1, (10, 10, 10))
		textpos = text.get_rect(centerx=background.get_width()/2)
		background.blit(text, textpos)

	screen.blit(background, (0, 0))
	pygame.display.flip()

	clock = pygame.time.Clock()
	H1 = Atom('H')
	H2 = Atom('H')
	O1 = Atom('O')
	atoms = pygame.sprite.RenderPlain((H1, H2, O1))
	active = None
	while 1:
		clock.tick(60)
		for event in pygame.event.get():
			if event.type == QUIT:
				return
			elif event.type == KEYDOWN and event.key == K_ESCAPE:
				return
			elif event.type == MOUSEBUTTONDOWN:
				for atom in atoms.sprites():
					if atom.clicked():
						active = atom
						break
			elif event.type is MOUSEBUTTONUP and active != None: 
				active.unclicked()
				active = None
		if active != None:
			for collition in pygame.sprite.spritecollide(active, atoms, False):
				if collition != active:
					if active.react(collition):
						collition.kill()	
					
		atoms.update()

		screen.blit(background, (0, 0))
		atoms.draw(screen)
		pygame.display.flip()


if __name__ == '__main__':
	main()
