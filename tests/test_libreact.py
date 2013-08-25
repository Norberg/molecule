import os
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

