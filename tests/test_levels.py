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
from libcml.Cml import Cml
from libcml import CachedCml
from molecule.Levels import Levels
from molecule import Universe

class TestLevels(unittest.TestCase):

	def testLevels(self):
		levels = Levels("data/levels")
		l = levels.next_level()
		expected = ['H+(g)', 'O(g)', 'O(g)', 'H+(g)', 'P(g)', 'F(g)', 'Al(s)']
		self.assertEqual(l.cml.molecules, expected)
		self.assertEqual(l.cml.victory_condition, ["H2O"])
		self.assertEqual(l.cml.objective, "Create a water molecule")
		self.assertEqual(l.cml.hint, "H + H + O => H2O")
		self.assertEqual(l.check_victory(), False)
		l.elements.add(Universe.create_elements(l.space, "H2O(g)"))
		self.assertEqual(l.check_victory(), True)

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
		levels = Levels("data/levels")
		for level in levels.level_iter():
			self.assertIsNotNone(level.cml.objective)
			self.assertEqual(level.check_victory(), False)

	def testDestroyElements(self):
		levels = Levels("data/levels")
		l = levels.next_level()
		l.elements.add(Universe.create_elements(l.space, ["O2(g)", "O2(g)", "CH4(g)"]))
		#self.assertEqual(l.elements, [])
		
