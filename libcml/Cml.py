import xml.etree.ElementTree as etree
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

class State:
	def __init__(self, name=None, enthalpy=None, entropy=None, ions=None):
		self.name = name
		self.enthalpy = enthalpy
		self.entropy = entropy
		self.ions = ions

	@property
	def ions_str(self):
		if self.ions is None:
			return ""
		str = ""
		for ion in self.ions:
			str +=","+ion
		return str[1:]

class Reaction:
	def __init__(self,reactants = None,products = None):
		self.reactants = reactants
		self.products = products

class Cml:
	NS = "{http://www.xml-cml.org/schema}"
		
	def treefind(self, xpath):
		return self.xmlfind(self.tree, xpath)	

	def xmlfind(self, document, xpath):
		element = document.find(xpath)
		if element is None:
			element = self.tree.find(self.NS + xpath)
		return element
	def parseReaction(self, reactionTag):
		reaction = Reaction()
		for part in reactionTag:
			if part.tag.endswith("productList"):
				reaction.products = self.parseReactionMolecules(part)
			elif part.tag.endswith("reactantList"):
				reaction.reactants = self.parseReactionMolecules(part)
		return reaction
		
	def parseReactionMolecules(self, moleculesTag):
		molecules = list()
		for molecule in moleculesTag:
			molecules.append(molecule.attrib["title"])
		return molecules
	def writeReaction(self, reaction, parrentTag):
		if reaction is None:
			return		
		tagReaction = etree.SubElement(parrentTag, "reaction")
		if reaction.products != None:
			tagProducts = etree.SubElement(tagReaction, "productList")
			self.writeReactionMolecules(reaction.products, tagProducts)
		if reaction.reactants != None:
			tagReactants = etree.SubElement(tagReaction, "reactantList")
			self.writeReactionMolecules(reaction.reactants, tagReactants)

	def writeReactionMolecules(self, products, parrentTag):
		for product in products:
			etree.SubElement(parrentTag, "molecule", {"title":product})
		

class Reactions(Cml):
	def __init__(self):
		self.tree = None
		self.reactions = list()

	def parse(self, filename):
		self.tree = etree.parse(filename)
		self.parseReactions(self.tree.getroot())
		

	def parseReactions(self, reactions):
		for reaction in reactions:
			r = self.parseReaction(reaction)
			self.reactions.append(r)
	
	def empty_cml(self):
		reactions = etree.Element("reactions")
		return etree.ElementTree(reactions)

	def write(self, filename):
		if self.tree is None:
			self.tree = self.empty_cml()
		
		self.writeReactions()
		self.tree.write(filename)		

	def writeReactions(self):
		reactionsTag = self.tree.getroot()
		for reaction in self.reactions:
			self.writeReaction(reaction, reactionsTag)
		
	def writeStates(self):
		states = self.treefind(self.STATES)
		if states is None:
			molecule = self.tree.getroot()
			states = etree.SubElement(molecule, "propertyList",
			                          {"title":"states"})
		else:
			states.clear() # Remove all old entires
			states.attrib["title"] = "states"

		for state in self.states.values():
			stateTag = etree.SubElement(states, "propertyList",
			                            {"title":state.name})
			self.writeEnthalpy(state, stateTag)
			self.writeEntropy(state, stateTag)
			self.writeIons(state.ions, stateTag)

class Molecule(Cml):
	ATOM_ARRAY = 'atomArray'
	BOND_ARRAY = 'bondArray'
	PROPERTY_LIST = "propertyList"
	STATES = PROPERTY_LIST+"/[@title='states']"
	MOLECULE = "molecule"

	def __init__(self):
		self.atoms = dict()
		self.bonds = list()
		self.states = dict()
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

	def parse(self, filename):
		etree.register_namespace("", self.NS)
		self.tree = etree.parse(filename)
		self.parseAtoms(self.treefind(self.ATOM_ARRAY))
		self.parseBonds(self.treefind(self.BOND_ARRAY))
		self.parseStates(self.treefind(self.STATES))
	
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
		if states == None:
			return
		for state in states:
			name = state.attrib["title"]
			new_state = State(name)
			self.states[name] = new_state
			for property in state:
				title = property.attrib["title"] 
				if title == "entropy":
					new_state.entropy = float(property[0].text)
				elif title == "enthalpy":
					new_state.enthalpy = float(property[0].text)
				elif title == "ions":
					new_state.ions = self.parseIons(property) 

	def parseIons(self, ions):
		reaction = self.parseReaction(ions[0])
		return reaction.products


	def empty_cml(self):
		molecule = etree.Element("molecule")
		atomArray = etree.SubElement(molecule, "atomArray")
		bondArray = etree.SubElement(molecule, "bondArray")
		return etree.ElementTree(molecule)

	def write(self, filename):
		if self.tree is None:
			self.tree = self.empty_cml()
		
		self.writeAtoms()
		self.writeBonds()
		self.writeStates()
		self.tree.write(filename)		
	
	def writeBonds(self):
		bondArray = self.treefind(self.BOND_ARRAY)
		bondArray.clear() # Remove all old entires
		for bond in self.bonds:
			attrib = {"atomRefs2" : bond.atomRefs2,
			          "order" : str(bond.bonds)}
			etree.SubElement(bondArray,"bond", attrib)

	def writeAtoms(self):
		atomArray = self.treefind(self.ATOM_ARRAY)
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

	def writeStates(self):
		states = self.treefind(self.STATES)
		if states is None:
			molecule = self.tree.getroot()
			states = etree.SubElement(molecule, "propertyList",
			                          {"title":"states"})
		else:
			states.clear() # Remove all old entires
			states.attrib["title"] = "states"

		for state in self.states.values():
			stateTag = etree.SubElement(states, "propertyList",
			                            {"title":state.name})
			self.writeEnthalpy(state, stateTag)
			self.writeEntropy(state, stateTag)
			self.writeIons(state.ions, stateTag)

	def writeEnthalpy(self,state, stateTag):
		if state.enthalpy is None:
			return
		tagEnthalpy = etree.SubElement(stateTag, "property",
		                               {"title": "enthalpy"})
		scalar = etree.SubElement(tagEnthalpy, "scalar",
		                          {"units":"units:molar_energy"})
		scalar.text = str(state.enthalpy)
	
	def writeEntropy(self,state, stateTag):
		if state.entropy is None:
			return
		tagEntropy = etree.SubElement(stateTag, "property",
		                               {"title": "entropy"})
		scalar = etree.SubElement(tagEntropy, "scalar",
		                          {"units":"units:molar_energy"})
		scalar.text = str(state.entropy)
	
	def writeIons(self, ions, parrentTag):
		if ions is None or len(ions) == 0:
			return
		r = Reaction(None, ions)
		tagIons = etree.SubElement(parrentTag, "property",
		                               {"title": "ions"})
		
		self.writeReaction(r, tagIons)
	
