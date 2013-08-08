import xml.etree.ElementTree as etree
import xml.dom.minidom as minidom

class Atom:
	def __init__(self):
		self.id = None
		self.elementType = None
		self.x = None
		self.y = None
		self.z = None

	@property
	def x_str(self):
		return str(self.x)	
	@property
	def y_str(self):
		return str(self.y)	
	@property
	def z_str(self):
		return str(self.z)	

class Bond:
	def __init__(self):
		""" Bond from atomA to atomB having nr of bonds"""
		self.atomA = None
		self.atomB = None
		self.bonds = None
	
	@property
	def atomRefs2(self):
		return self.atomA + " " + self.atomB	

class Molecule:
	ATOM_ARRAY = 'atomArray'
	BOND_ARRAY = 'bondArray'
	def __init__(self):
		self.atoms = dict()
		self.bonds = list()

	def printer(self):
		print "Atoms:"
		for atom in self.atoms.values():
			print atom.id, atom.elementType
		print "Bonds:"
		for bond in self.bonds:
			print bond.atomA, "->", bond.atomB, bond.bonds, "bonds"


	def parse(self, filename):
		etree.register_namespace("","http://www.xml-cml.org/schema")
		self.tree = etree.parse(filename)
		root = self.tree.getroot()
		for child in root.getchildren():
			if child.tag.endswith(self.ATOM_ARRAY):
				self.parseAtoms(child)
			elif child.tag.endswith(self.BOND_ARRAY):
				self.parseBonds(child)
			else:
				raise Exception("Unknown tag:" + child.tag)

	
	def parseAtoms(self,atoms):
		for atom in atoms:
			new = Atom()
			new.id = atom.attrib["id"]
			new.elementType = atom.attrib["elementType"]
			try:
				new.x = float(atom.attrib["x2"])
				new.y = float(atom.attrib["y2"])
			except KeyError:
				new.x = float(atom.attrib["x3"])
				new.y = float(atom.attrib["y3"])
				new.z = float(atom.attrib["z3"])
				
			self.atoms[new.id] = new
			
	def parseBonds(self,bonds):
		for bond in bonds:
			new = Bond()
			atomRefs = bond.attrib["atomRefs2"].split()
			new.atomA = atomRefs[0]
			new.atomB = atomRefs[1]
			new.bonds = bond.attrib["order"]
			self.bonds.append(new)
	
	def write(self, filename):
		self.writeAtoms()
		self.writeBonds()
		self.tree.write(filename)		
	
	def writeBonds(self):
		bondArray = self.tree.find(self.BOND_ARRAY)
		bondArray.clear() # Remove all old entires
		for bond in self.bonds:
			attrib = {"atomRefs2" : bond.atomRefs2,
			          "order" : bond.bonds}
			etree.SubElement(bondArray,"bond", attrib)

	def writeAtoms(self):
		atomArray = self.tree.find(self.ATOM_ARRAY)
		atomArray.clear() # Remove all old entires
		for atom in self.atoms.values():
			if atom.z is None:
				attrib = {"x2":atom.x_str,
				          "y2": atom.y_str}
			else:
				attrib = {"x3":atom.x_str,
				          "y3": atom.y_str,
				          "z3": atom.z_str}
			attrib["id"] = atom.id
			attrib["elementType"] = atom.elementType
			etree.SubElement(atomArray,"atom", attrib)

