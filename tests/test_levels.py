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
import unittest
from libcml import Cml
from libcml import CachedCml
from libreact.Reactor import Reactor
from molecule.Levels import Levels
from molecule import Universe
from molecule.Elements import Molecule
from molecule import CollisionTypes
import pyglet
import pymunk

class TestLevels(unittest.TestCase):
    def testLevels(self):
        levels = Levels("data/levels", window=WindowMock())
        l = levels.get_current_level()
        expected = ['H+(g)', 'O(g)', 'O(g)', 'H+(g)', 'P(g)', 'F(g)', 'Al(s)']
        self.assertEqual(l.cml.molecules, expected)
        self.assertEqual(l.cml.victory_condition, ["H2O"])
        self.assertEqual(l.cml.objective, "Create a water molecule")
        self.assertEqual(l.cml.hint, "H + H + O => H2O")
        self.assertEqual(l.victory(), False)
        batch = pyglet.graphics.Batch()
        l.elements.extend(Universe.create_elements(l.space, "H2O(g)", batch, None))
        victory_effect = l.hud.horizontal.victory
        victory_effect.put_element(l.elements.pop())
        self.assertEqual(l.victory(), True)

        l = levels.next_level()
        expected = ['H+(g)', 'O(g)', 'O(g)', 'H+(g)', 'OH-(aq)', 'CO2(g)', 'CH4(g)']
        self.assertEqual(l.cml.molecules, expected)
        self.assertEqual(l.cml.victory_condition, ['CO', 'H2', 'H2', 'H2'])
        self.assertEqual(l.cml.objective, "Create a CO and 3 H2 molecules")
        self.assertEqual(l.cml.hint, "H2O + CH4 + Heat => CO + 3H2")
        levels.current_level = 1000
        l = levels.next_level()
        self.assertEqual(l, None)

    def testAllLevels(self):
        levels = Levels("data/levels", window=WindowMock())
        space, batch = createSpaceAndBatchMock()
        for level in levels.level_iter():
            self.assertIsNotNone(level.cml.objective)
            self.assertEqual(level.victory(), False)
            Universe.create_elements(level.space, level.cml.inventory, level.batch, None)
    
    def testDestroyElements(self):
        levels = Levels("data/levels", window=WindowMock())
        l = levels.next_level()
        batch = pyglet.graphics.Batch()
        l.elements.extend(Universe.create_elements(l.space,
                                                   ["O2(g)", "O2(g)", "CH4(g)"],
                                                   batch, None))
        #self.assertEqual(l.elements, [])

    def testGetCollidingMolecules(self):
        level1 = getLevel1()
        space, batch = createSpaceAndBatchMock()
        OH = Molecule("OH-(aq)", space, batch)
        H = Molecule("H+(g)", space, batch)
        OH.creation_time = 0
        H.creation_time = 0
        collisions = createCollisionsMock(OH, H)
        collidingMolecules = level1.get_colliding_molecules(collisions)
        self.assertEqual([OH, H], collidingMolecules)

    def testGetReactingMolecules(self):
        level1 = getLevel1()
        space, batch = createSpaceAndBatchMock()
        OH = Molecule("OH-(aq)", space, batch)
        Al = Molecule("Al(s)", space, batch)
        H = Molecule("H+(g)", space, batch)
        H_ = Molecule("H+(g)", space, batch)
        OH.creation_time = 0
        Al.creation_time = 0
        H.creation_time = 0
        H_.creation_time = 0
        collisions = createCollisionsMock(OH, Al, H, H_)
        reaction = setupSimpleReactor().react([H.state_formula,OH.state_formula])
        reactingMolecules = level1.get_molecules_in_reaction(collisions, reaction)
        self.assertEqual([OH, H], reactingMolecules,)

    def testCollisionReaction(self):
        level1 = getLevel1()
        space, batch = createSpaceAndBatchMock()
        OH = Molecule("OH-(aq)", space, batch)
        Al = Molecule("Al(s)", space, batch)
        H = Molecule("H+(g)", space, batch)
        H_ = Molecule("H+(g)", space, batch)
        OH.creation_time = 0
        Al.creation_time = 0
        H.creation_time = 0
        H_.creation_time = 0
        collisions = createCollisionsMock(OH, Al, H, H_)
        reaction = level1.react(collisions,[])
        self.assertEqual(reaction.reactants, ['H+(g)', 'H+(g)'])
        self.assertEqual(reaction.products, ['H2(g)'])

    def testSulfuricAcidReaction(self):
        level1 = getLevel1()
        space, batch = createSpaceAndBatchMock()
        H2SO4 = Molecule("H2SO4(l)", space, batch)
        NaCl = Molecule("NaCl(s)", space, batch)
        NaCl_ = Molecule("NaCl(s)", space, batch)
        H2SO4.creation_time = 0
        NaCl.creation_time = 0
        NaCl_.creation_time = 0
        collisions = createCollisionsMock(H2SO4, NaCl, NaCl_)
        reaction = level1.react(collisions,[])
        self.assertEqual(reaction.reactants, ['H2SO4(l)', 'NaCl(s)', 'NaCl(s)'])
        self.assertEqual(reaction.products, ['HCl(g)', 'HCl(g)', 'Na2SO4(s)'])

    def testSulfuricAcidNoReaction(self):
        level1 = getLevel1()
        space, batch = createSpaceAndBatchMock()
        H2SO4 = Molecule("H2SO4(l)", space, batch)
        NaCl = Molecule("NaCl(s)", space, batch)
        H2SO4.creation_time = 0
        NaCl.creation_time = 0
        collisions = createCollisionsMock(H2SO4, NaCl)
        reaction = level1.react(collisions,[])
        self.assertEqual(reaction, None)

    def testVictoryEffect(self):
        level1 = getLevel1()
        victory_effect = level1.hud.horizontal.victory
        level1.create_elements(["CH4(g)"], pos = (200,300))
        level1.create_elements(["H2O(g)"], pos = (300,300))
        level1.update()

        level1.handle_element_pressed(234, 300)
        self.assertIsNotNone(level1.mouse_spring)
        level1.handle_element_released(50, 50, None, None)
        self.assertIsNone(level1.mouse_spring)
        self.assertEqual(victory_effect.content, {})
        self.assertEqual(victory_effect.victory(), False)
        self.assertEqual(victory_effect.progress_text(), "0/1 H2O")

        level1.handle_element_pressed(300, 300)
        self.assertIsNotNone(level1.mouse_spring)
        level1.handle_element_released(50, 50, None, None)
        self.assertIsNone(level1.mouse_spring)
        self.assertEqual(victory_effect.content, {"H2O":1})
        self.assertEqual(victory_effect.victory(), True)
        self.assertEqual(victory_effect.progress_text(), "1/1 H2O")


def setupSimpleReactor():
    r1 = Cml.Reaction(["H2SO4(l)","NaCl(s)", "NaCl(s)"],
                      ["HCl(g)", "HCl(g)", "Na2SO4(s)"])
    r2 = Cml.Reaction(["OH-","H+"], ["H2O(l)"])
    return Reactor([r1,r2])

def getLevel1():
    levels = Levels("data/levels", window=WindowMock())
    level1 = levels.get_current_level()
    return level1

def createCollisionsMock(*molecules):
    collision = list()
    for molecule in molecules:
        collision.append(CollisionMock(molecule))
    return collision

def createSpaceAndBatchMock():
    return(SpaceMock(), BatchMock())

class CollisionMock():
    def __init__(self, molecule):
        self.molecule = molecule
        self.collision_type = CollisionTypes.ELEMENT
        self.shape = pymunk.Circle(None, 16);

class SpaceMock():
    def add(*args):
        pass

class BatchMock():
    def add(*args):
        return VerticeMock()

class VerticeMock():
    def __init__(self):
        self.vertices = list()
        self.colors = list()

class WindowMock():
    def __init__(self):
        self.width = 1024
        self.height = 768
    def get_size(self):
        return (self.width, self.height)
    def push_handlers(self, *arg, **kwargs):
        pass
    def set_handlers(self, *arg, **kwargs):
        pass
