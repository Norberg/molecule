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
import glob, random
import copy
import re
import pymunk
import pygame
from . import PyGameUtil,util
from .Molecule import Molecule, MoleculeSprite
from molecule import Config
from libreact.Reactor import Reactor
from libcml import Cml

class Universe:
	"""Universe contains all fundamental particles and laws needed to get the universe to spin"""
	def __init__(self):
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
		reaction = self.reactor.react(reactants, temp)
		
		if reaction == None:
			if Config.current.DEBUG: print("Did not react:", reactants)
			return None
		else:		
			print(reaction.reactants, "+", effect_names, "->", reaction.products)
			return reaction
		
def create_elements(space, elements, pos=None):
	""" Create a set of elements
	body: shape to attach molecule to
	element: list of elements to create
	pos : position of the new element
	"""	
	list_of_elements = list()
	if pos != None:
		x, y = pos

	if isinstance(elements, str):
		elements = [elements] #elements is a string, wrap it in a list not to confuse for
	for element in elements:
		if pos != None and len(elements) > 1:
			pos = (x + random.randint(-50,50), y + random.randint(-50, 50))
		molecule = Molecule(element)
		list_of_elements.append(MoleculeSprite(molecule, space,  pos))
	return tuple(list_of_elements)


universe = None
def createUniverse():
	global universe
	universe = Universe()
