import Universe
import Molecule
import Config

class Reaction:
	def __init__(self,reactants,products, areas = list()):
		self.verify(reactants)
		self.verify(products)
		self.reactants = reactants
		self.products = products
		self.areas = areas

	def deltaEnthalpy(self):
		enthalpyReactans = self.sumEnthalpy(self.reactants)
		enthalpyProducts = self.sumEnthalpy(self.products)
		deltaEnthalpy = enthalpyProducts - enthalpyReactans
		if Config.current.DEBUG:
			print "deltaH = sumProductsH - sumReactansH"
			print deltaEnthalpy, "=", enthalpyProducts, "-", enthalpyReactans
	
		return deltaEnthalpy

	def deltaEntropy(self):
		entropyReactans = self.sumEntropy(self.reactants) / 1000.0 #j -> kj
		entropyProducts = self.sumEntropy(self.products) / 1000.0 #j -> kj
		deltaEntropy = entropyProducts - entropyReactans 
		
		if Config.current.DEBUG:
			print "deltaS = sumProductsS - sumReactansS"
			print deltaEntropy, "=", entropyProducts, "-", entropyReactans
		return deltaEntropy

	def isSpontaneous(self, K = 298):
		deltaEnthalpy = self.deltaEnthalpy()
		deltaEntropy = self.deltaEntropy()	
		free_energy = deltaEnthalpy - K * deltaEntropy

		if Config.current.DEBUG:
			print "deltaG = deltaH - T * deltaS"
			print free_energy, "=", deltaEnthalpy, "-", K, "*", deltaEntropy

		return free_energy < 0

	def sumEntropy(self, elements):
		sum = 0
		for molecule in self.toMolecules(elements):
			sum += molecule.entropy
		return sum
		
	def sumEnthalpy(self, elements):
		sum = 0
		for molecule in self.toMolecules(elements):
			sum += molecule.enthalpy
		return sum
	
	def toMolecules(self,elements):
		for element in elements:
			yield Universe.universe.molecule_table(element)

	"""Sanity check of symbol name, make sure no zeros have been used by mistake"""
	def verify(self, elements):
		for element in elements:
			if "0" in element:
				raise Exception("Tried to create reaction with invalid values")
