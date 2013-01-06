import time, os, pygame,random
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
				return "O2"
			elif b == 'H2':
				return "H2O"
		elif a == 'H':
			if b == 'H':
				return "H2"
			elif b == 'OH':
				return "H2O"
		elif a == "CH4":
			if b == "H2O":
				return ["CO"] + 3*["H2"]
		
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
		elif molecule == "O2":
			layout[(1,1)] = 'O'	
			layout[(2,1)] = 'O'	
		elif molecule == "CO":
			layout[(1,1)] = 'C'	
			layout[(2,1)] = 'O'
		elif molecule == "CO2":
			layout[(1,1)] = 'O'	
			layout[(2,1)] = 'C'
			layout[(3,1)] = 'O'	
		elif molecule == "CH4":
			layout[(2,2)] = 'C'	
			layout[(2,1)] = 'H'	
			layout[(1,2)] = 'H'	
			layout[(2,3)] = 'H'	
			layout[(3,2)] = 'H'	
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
		if direction == "bottom":
			return (x+1, y+2)
		elif direction == "left":
			return (x-2, y)
				
	def create_links(self, layout):
		links = pygame.Surface((160,160), 0, self.create_atom('O', copy=False))
		for pos in layout.keys():
				x,y = pos
				if layout.has_key((x, y+1)): #Bottom
					link_pos = self.pos2cord_link(pos, "bottom")
					links.blit(self.link_bottom, link_pos)
				if layout.has_key((x-1, y)): #Left
					link_pos = self.pos2cord_link(pos, "left")
					links.blit(self.link_left, link_pos)
		return links

	def create_molecule(self, symbol):
		if self.is_atom(symbol):
			return self.create_atom(symbol)

		layout = self.molecule_table(symbol)
		if layout != None:
			links = self.create_links(layout)
			molecule = pygame.Surface((160,160), 0, links)
			molecule.blit(links, (0,0))
			for pos in layout.keys():
				symbol = layout[pos]
				atom = self.create_atom(symbol, copy=False)
				molecule.blit(atom, self.pos2cord(pos))
			return molecule

	def is_atom(self, symbol):
		if len(symbol) == 1 and symbol.isalpha(): # H, O, F etc.
			return True
		elif len(symbol) == 2 and symbol.isalpha() and symbol[1].islower(): #Fe, Mg, Na etc.
			return True
		elif len(symbol) == 3 and symbol.isalpha() and symbol[1:3].islower(): #Uut, Uup, Uus etc.
			return True
		else:
			return False

	def create_elements(self, elements, pos=None):
		list_of_elements = list()
		if pos != None:
			x, y = pos

		if isinstance(elements, basestring):
			elements = [elements] #elements is a string, wrap it in a list not to confuse for
		for element in elements:
			if pos != None and len(elements) > 1:
				pos = (x + random.randint(-50,50), y + random.randint(-50, 50))
			list_of_elements.append(Element(element, pos))
		return tuple(list_of_elements)

universe = Universe()

class Element(pygame.sprite.Sprite):
	"""Element - The universal building block of atoms and molecules"""
	def __init__(self, symbol, pos=None):
		pygame.sprite.Sprite.__init__(self)
		self.symbol = symbol
		self.image = universe.create_molecule(symbol)
		self.rect = self.image.get_bounding_rect()
		self.active = False
		if pos == None:
			self.rect.move_ip(random.randint(10, 600), random.randint(10, 400))
		else:
			self.rect.move_ip(pos)
				

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
			print "Created:", reaction, "from ", self.symbol,"+", other.symbol
			return universe.create_elements(reaction, pos = self.rect.midtop)

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
	e = universe.create_elements(["H", "O", "OH", "O", "H", "CO2", "CH4"])
	elements = pygame.sprite.RenderUpdates(e)
	active = None
	while 1:
		clock.tick(60)
		for event in pygame.event.get():
			if event.type == QUIT:
				return
			elif event.type == KEYDOWN and event.key == K_ESCAPE:
				return
			elif event.type == MOUSEBUTTONDOWN:
				for element in reversed(elements.sprites()):
					if element.clicked():
						active = element
						break
			elif event.type is MOUSEBUTTONUP and active != None: 
				active.unclicked()
				active = None

		if active != None:
			for collition in pygame.sprite.spritecollide(active, elements, False):
				if collition != active:
					new_elements = active.react(collition)
					if new_elements != None:
						collition.kill()
						active.kill()
						active = None
						elements.add(new_elements)
					break	
		elements.update()
		screen.blit(background, (0, 0))
		#if active != None:
		#	pygame.draw.rect(screen, pygame.color.Color("black"), active.rect)
		elements.draw(screen)
		pygame.display.flip()


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		pass
	from guppy import hpy
	h = hpy()
	print h.heap()
