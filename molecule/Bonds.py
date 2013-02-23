import PyGameUtil

class Bond:
	def __init__(self, from_pos, to_pos, nr_of_bonds = 1):
		self.from_pos = from_pos
		self.to_pos = to_pos
		self.nr_of_bonds = nr_of_bonds

class BondImage:
	def __init__(self, path, is_vertical=False):
		self.bond = list()
		self.bond.append(PyGameUtil.loadImage(path))
		
		if is_vertical:
			b2pos1 = (-3,0)
			b2pos2 = (3,0)
			b3pos1 = (-5,0)
			b3pos2 = (0,0)
			b3pos3 = (5,0)
		else:
			b2pos1 = (0,-3)
			b2pos2 = (0,3)
			b3pos1 = (0,-5)
			b3pos2 = (0,0)
			b3pos3 = (0,5)
		
		b = PyGameUtil.createSurface(64)	
		b.blit(self.get(1), b2pos1)
		b.blit(self.get(1), b2pos2)
		self.bond.append(b)

		b = PyGameUtil.createSurface(64)	
		b.blit(self.get(1), b3pos1)
		b.blit(self.get(1), b3pos2)
		b.blit(self.get(1), b3pos3)
		self.bond.append(b)

	def get(self, bond):
		return self.bond[bond-1]		

horizontal = None
vertical = None
northwest = None
southwest = None

def init__bonds():
	global horizontal
	global vertical
	global northwest
	global southwest
	horizontal = BondImage("img/bond-horizontal.png")
	vertical = BondImage("img/bond-vertical.png", is_vertical = True)
	northwest = BondImage("img/bond-northwest.png")
	southwest = BondImage("img/bond-southwest.png")
