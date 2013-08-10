import xml.etree.ElementTree as etree
import xml.dom.minidom as minidom
import operator

class Atom:
	def __init__(self, id=None, element=None, charge=None, x=None, y=None, z=None):
		self.id = id
		self.elementType = element
		self.formalCharge = charge
		self.x = x
		self.y = y
		self.z = z

	@property
	def pos(self):
		return (self.x, self.y)		

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
	def __init__(self, atomA = None, atomB = None, bonds = None):
		""" Bond from atomA to atomB having nr of bonds"""
		self.atomA = atomA
		self.atomB = atomB
		self.bonds = bonds
	
	@property
	def atomRefs2(self):
		return self.atomA.id + " " + self.atomB.id

class Molecule:
	ATOM_ARRAY = 'atomArray'
	BOND_ARRAY = 'bondArray'
	PROPERTY_LIST = "propertyList"
	STATES = PROPERTY_LIST+"/[@title='states']"
	NS = "{http://www.xml-cml.org/schema}"

	def __init__(self):
		self.atoms = dict()
		self.bonds = list()
		self.tree = None

	def getDigits(self, string):
		temp = [s for s in string if s.isdigit()]
		string = ""
		for t in temp:
			string += t
		return int(string)

	@property
	def atoms_sorted(self):
		return sorted(self.atoms.values(), key=lambda x:self.getDigits(x.id)) 

	def printer(self):
		print "Atoms:"
		for atom in self.atoms.values():
			print atom.id, atom.elementType
		print "Bonds:"
		for bond in self.bonds:
			print bond.atomA.id, "->", bond.atomB.id, bond.bonds, "bonds"

	def min_pos(self):
		min_x = min(self.atoms.values(), key=lambda a:a.x).x
		min_y = min(self.atoms.values(), key=lambda a:a.y).y
		min_z = min(self.atoms.values(), key=lambda a:a.z).z
		return (min_x, min_y, min_z)

	def max_pos(self):
		max_x = max(self.atoms.values(), key=lambda a:a.x).x
		max_y = max(self.atoms.values(), key=lambda a:a.y).y
		max_z = max(self.atoms.values(), key=lambda a:a.z).z
		return (max_x, max_y, max_z)

	def normalize_pos(self):
		""" normalize position to only be positive """
		min_x, min_y, min_z = self.min_pos()
		adj_x = min(0, min_x)
		adj_y = min(0, min_y)
		adj_z = min(0, min_z)
		
		if adj_z != 0 or adj_y != 0 or adj_x != 0:
			for atom in self.atoms.values():
				atom.x -= adj_x
				atom.y -= adj_y
				if atom.z is not None:
					atom.z -= adj_z
	def xmlfind(self, xpath):
		element = self.tree.find(xpath)
		if element is None:
			element = self.tree.find(self.NS + xpath)
		return element

	def parse(self, filename):
		etree.register_namespace("", self.NS)
		self.tree = etree.parse(filename)
		self.parseAtoms(self.xmlfind(self.ATOM_ARRAY))
		self.parseBonds(self.xmlfind(self.BOND_ARRAY))
		self.parseStates(self.xmlfind(self.STATES))
	
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
			try:
				new.formalCharge = int(atom.attrib["formalCharge"])
			except KeyError:
				pass	
			self.atoms[new.id] = new
			
	def parseBonds(self,bonds):
		for bond in bonds:
			new = Bond()
			atomRefs = bond.attrib["atomRefs2"].split()
			new.atomA = self.atoms[atomRefs[0]]
			new.atomB = self.atoms[atomRefs[1]]
			new.bonds = int(bond.attrib["order"])
			self.bonds.append(new)

	def parseStates(self, states):
		pass
	def empty_cml(self):
		molecule = etree.Element("molecule")
		atomArray = etree.SubElement(molecule, "atomArray")
		bondArray= etree.SubElement(molecule, "bondArray")
		return etree.ElementTree(molecule)

	def write(self, filename):
		if self.tree is None:
			self.tree = self.empty_cml()
		
		self.writeAtoms()
		self.writeBonds()
		self.tree.write(filename)		
	
	def writeBonds(self):
		bondArray = self.tree.find(self.BOND_ARRAY)
		bondArray.clear() # Remove all old entires
		for bond in self.bonds:
			attrib = {"atomRefs2" : bond.atomRefs2,
			          "order" : str(bond.bonds)}
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
			if atom.formalCharge is not None:
				attrib["formalCharge"] = str(atom.formalCharge)

			attrib["id"] = atom.id
			attrib["elementType"] = atom.elementType
			etree.SubElement(atomArray,"atom", attrib)

