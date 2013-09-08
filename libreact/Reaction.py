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
import re
from libcml import CachedCml

class Reaction:
	def __init__(self, cml, reacting_elements):
		self.cml = cml
		self.products = cml.products
		self.reactants = list(cml.reactants)
		self.addStateToReactants(reacting_elements)
		verify(self.products)	
		verify(self.reactants)	

	
	def addStateToReactants(self, reactants):
		""" Take a list of reactans with state to populate the reaction with the same info"""
		for reactant in reactants:
			reactant_without_state = remove_state(reactant) 
			if reactant_without_state in self.reactants:
				self.reactants.remove(reactant_without_state)
				self.reactants.append(reactant)	

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
