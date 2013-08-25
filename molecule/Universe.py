import glob, random
import copy
import re
import pymunk
import pygame
import PyGameUtil,util,Bonds
from Molecule import Molecule, MoleculeSprite
import State
import Config
from libreact.Reactor import Reactor
from libcml import Cml

class Universe:
	"""Universe contains all fundamental particles and laws needed to get the universe to spin"""
	def __init__(self):
		print "Universe is initilazing" 
		self.moelcules = dict()
		cml = Cml.Reactions()
		cml.parse("data/reactions.cml")
		self.reactor = Reactor(cml.reactions)

	def react(self, reactants, effects):
		if len(reactants) < 2:
			return
		temp = 298
		effect_names = list()
		for effect in effects:
			effect_names.append(effect.name)
			if effect.name == "Fire":
				temp = effect.temp
		reaction = self.reactor.react(reactants)
		
		if reaction == None:
			if Config.current.DEBUG: print "Did not react:", reactants
			return None
		else:		
			print reaction.reactants, "+", effect_names, "->", reaction.products
			return reaction
		
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
			molecule = Molecule(element)
			list_of_elements.append(MoleculeSprite(molecule, space,  pos))
		return tuple(list_of_elements)


universe = None
print "univers = None"
def createUniverse():
	global universe
	universe = Universe()
	print "Creaded the Universe"
