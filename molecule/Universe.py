import glob, random
import copy
import re
import pymunk
import pygame
import PyGameUtil,util,Bonds
from Reaction import Reaction
from Molecule import Molecule, MoleculeSprite
import data.reactions
import data.atoms
import data.molecules
import State
import Config

class Universe:
	"""Universe contains all fundamental particles and laws needed to get the universe to spin"""
	def __init__(self):
		print "Universe is initilazing" 
		self.moelcules = dict()
		self.__init__data()
		Bonds.init__bonds()

	def __init__data(self):
		self.reactions =  data.reactions.reactions
		self.molecule_layouts = data.atoms.atom_layouts
		self.molecule_layouts.update(data.molecules.molecule_layouts)

	def reaction_table(self, reactants, effects):
		reactants_without_state = self.list_without_state(reactants)
		for reaction in self.reactions:
			if util.sublist_in_list(reaction.reactants, reactants_without_state):
				#all elements needed for the reaction exists in the reacting elements
				temp = 298
				effect_names = list()
				for effect in effects:
					effect_names.append(effect.name)
					if effect.name == "Fire":
						temp = effect.temp
				reaction.addStateToReactants(reactants)	
				print reaction.reactants, "+", effect_names, "->", reaction.products
				if reaction.isSpontaneous(temp):
					return reaction
				else:
					print "reaction was not spontanues at this temperature"
		
	def molecule_state_table(self, molecule_formula):
		"""Returns a molecule with same state as molecule_formula"""
		formula, state = self.split_state(molecule_formula)
		molecule = self.molecule_table(formula)
		molecule.change_state(state)
		return molecule	
	
	def molecule_table(self, molecule):
		"""Return a molecule from internal table without state """
		if self.molecule_layouts.has_key(molecule):
			return self.molecule_layouts[molecule]
		else:
			raise Exception("No layout found for:" + molecule)

	def create_molecule(self, molecule_form):
		formula, state = self.split_state(molecule_form)
		molecule = copy.copy(self.molecule_table(formula)) #TODO implement .__copy__ that only copies the current_state variable
		molecule.change_state(state)
		return molecule

	def split_state(self, molecule):
		"""return formula, state"""
		#regexp extract molecule and state from H20(aq)
		groups = re.search("(\S+)\((.*)\)", molecule)
		formula = groups.group(1)
		state = groups.group(2)
		return formula, state

	def remove_state(self, molecule):
		return self.split_state(molecule)[0]

	def list_without_state(self, molecules):
		"""Return a list of molecules without any state """
		without_state = list()
		for molecule in molecules:
			without_state.append(self.remove_state(molecule))
		return without_state

	def create_elements(self, space, elements, pos=None):
		""" Create a set of elements
		body: shape to attach molecule to
		element: list of elements to create
		pos : position of the new element
		"""	
		list_of_elements = list()
		if pos != None:
			x, y = pos

		if isinstance(elements, basestring):
			elements = [elements] #elements is a string, wrap it in a list not to confuse for
		for element in elements:
			if pos != None and len(elements) > 1:
				pos = (x + random.randint(-50,50), y + random.randint(-50, 50))
			print element
			molecule = self.create_molecule(element)
			list_of_elements.append(MoleculeSprite(molecule, space,  pos))
		return tuple(list_of_elements)

	def react(self, elements, areas):
		if len(elements) < 2:
			return
		if Config.current.DEBUG: print "Trying to see if some of this react:", elements
		reaction = self.reaction_table(elements, areas)
		if reaction != None:
			return reaction

universe = None
print "univers = None"
def createUniverse():
	global universe
	universe = Universe()
	print "Creaded the Universe"
