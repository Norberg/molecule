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
import random
import time
from molecule.Elements import Molecule
from molecule import Config
from libreact.Reactor import Reactor
from libreact import Reaction
from libcml import Cml

class Universe:
    """Universe contains all fundamental particles and laws needed to get the universe to spin"""
    def __init__(self):
        self.moelcules = {}
        cml = Cml.Reactions()
        cml.parse("data/reactions")
        self.reactor = Reactor(cml.reactions)

    def react(self, reactants, effects):
        if len(reactants) == 0:
            return
        elif len(reactants) == 1 and Config.current.DEBUG:
            # Check if decomposition reaction, might be a bit innificient
            # and also relies on self collision within the molecule
            # Self colltions should optimaly be handled by the physics engine instead
            print(f"Single reactant: {reactants}")

        temp = 298
        effect_names = list()
        energy_source = list()
        for effect in effects:
            effect_names.append(effect.name)
            if effect.supports("temp"):
                temp = effect.temp
            if effect.supports("energy_source"):
                energy_source.append(effect.energy_source)
        reaction = self.reactor.react(reactants, temp, energy_source=energy_source)

        if reaction == None:
            if Config.current.DEBUG: print(F"Did not react(T={temp}):", reactants)
            return None
        else:
            if Config.current.DEBUG:
                print(reaction.reactants, "+", effect_names, "->", reaction.products)
            return reaction

def create_elements(space, elements, batch, pos=None):
    """ Create a set of elements
    body: shape to attach molecule to
    element: list of elements to create
    pos : position of the new element
    """
    list_of_elements = list()
    if pos != None:
        x, y = pos

    if isinstance(elements, str):
        #elements is a string, wrap it in a list not to confuse for
        elements = [elements]

    for element in elements:
        if pos != None and len(elements) > 1:
            pos = (x + random.randint(-50,50), y + random.randint(-50, 50))
        list_of_elements.append(Molecule(element, space, batch, pos))

    return list_of_elements

universe = Universe()
