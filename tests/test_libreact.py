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
import libcml.Cml as Cml
from libreact.Reaction import Reaction
from libreact.Reactor import sublist_in_list
from libreact.Reactor import Reactor

class TestReact(unittest.TestCase):

	def setupSimpleReactor(self):
		r1 = Cml.Reaction(["O","H+"], ["OH-(aq)"])
		r2 = Cml.Reaction(["O","O"], ["O2(g)"])
		return Reactor([r1,r2])
	
	def setupRealReactor(self):
		cml = Cml.Reactions()
		cml.parse("data/reactions.cml")
		reactor = Reactor(cml.reactions)
		return reactor

	def testSublistInList(self):
		self.assertTrue(sublist_in_list("abcd", "abcdefg"))
		self.assertTrue(sublist_in_list("abcd", "bdeafbcg"))
		self.assertFalse(sublist_in_list("aabcd", "abcdefg"))
		self.assertFalse(sublist_in_list("abbcd", "abcdefg"))

	def testReactorInternals(self):
		reactor = self.setupSimpleReactor()
		reactants = ["O(g)", "O(g)"]
		find = reactor.find_reactions(reactants)
		self.assertEqual(find.reactants, ["O", "O"])	
		self.assertEqual(find.products, ["O2(g)"])	
		reaction = Reaction(find, reactants)
		self.assertAlmostEqual(reaction.deltaEntropy(), -0.117)
		self.assertAlmostEqual(reaction.deltaEnthalpy(), -498)
		self.assertTrue(reaction.isSpontaneous())	
		self.assertTrue(reaction.isSpontaneous(K = 0))	
		self.assertFalse(reaction.isSpontaneous(K = 5000))	

	def testSimpleReaction(self):	
		reactor = self.setupSimpleReactor()
		reaction = reactor.react(["O(g)", "O(g)"])
		self.assertTrue(reaction.isSpontaneous())
		reaction = reactor.react(["C(s)", "O(g)"])
		self.assertEqual(reaction, None)
		reaction = reactor.react(["H+(g)", "O(g)"])
		self.assertTrue(reaction.isSpontaneous())
		reaction = reactor.react(["H+(g)", "O(g)", "P(g)"])
		self.assertTrue(reaction.isSpontaneous())
		reaction = reactor.react(["O(g)"])
		self.assertEqual(reaction, None)

	def testComplexReactions(self):
		reactor = self.setupRealReactor()
		reaction = reactor.react(["CH4(g)", "H2O(g)"], K=1000)
		self.assertEqual(reaction.products, ["CO(g)", "H2(g)", "H2(g)", "H2(g)"])
		reaction = reactor.react(["H2SO4(aq)", "NaCl(s)", "NaCl(s)"])
		self.assertEqual(reaction.products, ["HCl(g)", "HCl(g)", "Na2SO4(s)"])

	def testExtraReactants(self):
		reactor = self.setupRealReactor()
		reaction = reactor.react(["H+(g)", "H+(g)", "H+(g)"])
		self.assertEqual(reaction.products, ["H2(g)"])
		self.assertEqual(reaction.reactants, ["H+(g)", "H+(g)"])
