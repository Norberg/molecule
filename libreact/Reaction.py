import re
from libcml import CachedCml

class Reaction:
	def __init__(self, cml, reactants):
		self.cml = cml
		self.products = cml.products
		self.reactants = reactants
		verify(self.products)	
		verify(self.reactants)	

	def deltaEnthalpy(self):
		enthalpyReactans = self.sumEnthalpy(self.reactants)
		enthalpyProducts = self.sumEnthalpy(self.products)
		deltaEnthalpy = enthalpyProducts - enthalpyReactans
		return deltaEnthalpy

	def deltaEntropy(self):
		entropyReactans = self.sumEntropy(self.reactants) / 1000.0 #j -> kj
		entropyProducts = self.sumEntropy(self.products) / 1000.0 #j -> kj
		deltaEntropy = entropyProducts - entropyReactans 
		return deltaEntropy

	def isSpontaneous(self, K = 298):
		deltaEnthalpy = self.deltaEnthalpy()
		deltaEntropy = self.deltaEntropy()	
		free_energy = deltaEnthalpy - K * deltaEntropy
		return free_energy < 0

	def sumEntropy(self, elements):
		sum = 0
		for molecule in self.getStates(elements):
			sum += molecule.entropy
		return sum
		
	def sumEnthalpy(self, elements):
		sum = 0
		for molecule in self.getStates(elements):
			sum += molecule.enthalpy
		return sum
	
	def getMolecule(self,element):
		no_state = remove_state(element)
		return CachedCml.getMolecule(no_state)

	def getStates(self, elements):
		for element in elements:
			molecule = self.getMolecule(element)
			formula, state = split_state(element)
			s = molecule.get_state(state)
			if s is None:
				raise Exception("Tried to read non existing state:(" 
				                 + state + ") for: "+ formula)
			else:
				yield s	
	

def split_state(molecule):
	"""return formula, state"""
	#regexp extract molecule and state from H20(aq)
	groups = re.search("(\S+)\((.*)\)", molecule)
	formula = groups.group(1)
	state = groups.group(2)
	return formula, state

def remove_state(molecule):
	return split_state(molecule)[0]

def verify(elements):
	"""Sanity check of symbol name, make sure no zeros have been used by mistake"""
	for element in elements:
		if "0" in element:
			raise Exception("Tried to create reaction with invalid values")

def list_without_state(molecules):
	"""Return a list of molecules without any state """
	without_state = list()
	for molecule in molecules:
		without_state.append(remove_state(molecule))
	return without_state
