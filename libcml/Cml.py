# Molecule - a chemical reaction puzzle game
# Copyright (C) 2013 Simon Norberg <simon@pthread.se>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
	STATE_MAP = {"Aqueous":"aq", "Solid":"s", "Gas":"g", "Liquid":"l"}
	def __init__(self, name=None, enthalpy=None, entropy=None, ions=None):
		self.name = name
		self.enthalpy = enthalpy
		self.entropy = entropy
		self.ions = ions

	@property
	def short(self):
		return self.STATE_MAP[self.name]

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

class Effect:
	def __init__(self, title = None, value = None, x2 = None, y2 = None):
		self.title = title
		self.value = value
		self.x2 = x2
		self.y2 = y2

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
				reaction.products = self.parseMoleculeList(part)
			elif part.tag.endswith("reactantList"):
				reaction.reactants = self.parseMoleculeList(part)
		return reaction
		
	def parseMoleculeList(self, moleculesTag):
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
	
	def parseText(self, tagname):
		tag = self.treefind(tagname)
		return tag.attrib["text"]
		

class Level(Cml):
	MOLECULE_LIST = "moleculeList"
	EFFECT_LIST = "effectList"
	VICTORY_CONDITION = "victoryCondition"
	OBJECTIVE = "objective"
	HINT = "hint"

	def __init__(self):
		self.tree = None
		self.molecules = list()
		self.effects = list()
		self.objective = None
		self.victory_condition = list()
		self.hint = None

	def parse(self, filename):
		self.tree = etree.parse(filename)
		molecule_list_tag = self.treefind(self.MOLECULE_LIST)
		self.molecules = self.parseMoleculeList(molecule_list_tag)

		victory_tag = self.treefind(self.VICTORY_CONDITION)
		self.victory_condition = self.parseMoleculeList(victory_tag)

		effect_tag = self.treefind(self.EFFECT_LIST)
		self.parseEffectList(effect_tag)

		self.objective = self.parseText(self.OBJECTIVE)
		self.hint = self.parseText(self.HINT)
	
	def parseEffectList(self, effect_list_tag):
		for effect_tag in effect_list_tag:
			effect = self.parseEffect(effect_tag)
			self.effects.append(effect)
		
	def parseEffect(self, effect_tag):
		effect = Effect()
		effect.title = effect_tag.attrib["title"]
		if effect_tag.attrib.has_key("value"):
			effect.value = float(effect_tag.attrib["value"])
		effect.x2 = float(effect_tag.attrib["x2"])
		effect.y2 = float(effect_tag.attrib["y2"])
		return effect

	def write(self, filename):
		raise NotImplementedError
	
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
	STATE_MAP = {"aq": "Aqueous", "s" : "Solid", "g" : "Gas", "l" : "Liquid"}
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


	def get_state(self, shortform):
		statename = self.STATE_MAP[shortform]
		if self.states.has_key(statename):
			return self.states[statename]
		else:
			return None
	
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
		""" normalize position to be as close to (0,0,[0]) as possible """
		adj_x, adj_y, adj_z = self.min_pos()
		
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
		if bonds == None:
			return
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
		if bondArray == None:
			return
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
	
