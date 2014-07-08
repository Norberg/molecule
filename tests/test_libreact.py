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

    def addState(self, stateless):
        default_order = ["Aqueous","Gas", "Liquid", "Solid"]
        statefull = list()
        for s in stateless:
            m = CachedCml.getMolecule(s)
            for k in default_order:
                if k in m.states:
                    state = m.states[k].short
                    break
            statefull.append(s+"(%s)"%state)
        return statefull

    def testSublistInList(self):
        self.assertTrue(sublist_in_list("abcd", "abcdefg"))
        self.assertTrue(sublist_in_list("abcd", "bdeafbcg"))
        self.assertFalse(sublist_in_list("aabcd", "abcdefg"))
        self.assertFalse(sublist_in_list("abbcd", "abcdefg"))

    def testReactorInternals(self):
        reactor = self.setupSimpleReactor()
        reactants = ["O(g)", "O(g)"]
        find = list(reactor.find_reactions(reactants))[0]
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

    def testPerformAllReactions(self):
        unsupported_reactions = [["C2H7NO3S(l)"]]
        tempranges = [0, 298, 1000, 2000, 4000, 8000, 50]
        reactor = self.setupRealReactor()
        for reaction in reactor.reactions:
            reactants = self.addState(reaction.reactants)
            expected_products = reaction.products
            result = None
            temp = None
            for temp in tempranges:
                result = reactor.react(reactants, temp)
                if result is not None and expected_products == result.products:
                    break # have found a temp where the expected reaction occurs
            if expected_products in unsupported_reactions:
                continue
            msg = "Expected reaction did not occur" + str(reactants) + "->" + \
                  str(expected_products) + " at:" + str(temp) + "K"
            self.assertNotEqual(result, None, msg)
            self.assertEqual(result.products, expected_products)
            self.assertEqual(result.reactants, reactants)

    def testPidgenonProcess(self):
        reactor = self.setupRealReactor()
        reaction = reactor.react(["Si(s)", "MgO(s)", "MgO(s)"], K=2300)
        self.assertEqual(reaction.products, ["SiO2(s)", "Mg(g)", "Mg(g)"])
        self.assertEqual(reaction.reactants, ["Si(s)", "MgO(s)", "MgO(s)"])

    def testSulfurDichloride(self):
        reactor = self.setupRealReactor()
        reaction = reactor.react(["S2Cl2(g)", "Cl2(g)"], trace=True)
        self.assertEqual(reaction.products, ["SCl2(g)", "SCl2(g)"])
        self.assertEqual(reaction.reactants, ["S2Cl2(g)", "Cl2(g)"])

    def testSulfurMustard(self):
        reactor = self.setupRealReactor()
        reaction = reactor.react(["SCl2(g)", "C2H4(g)", "C2H4(g)"], trace=True)
        self.assertEqual(reaction.products, ["C4H8Cl2S(g)"])
        self.assertEqual(reaction.reactants, ["SCl2(g)", "C2H4(g)", "C2H4(g)"])

    def testAmmonia(self):
        reactor = self.setupRealReactor()
        reaction = reactor.react(["NH3(g)", "H2O(g)"], trace=True, K=250)
        self.assertEqual(reaction.products, ["NH4+(aq)", "OH-(aq)"])
        self.assertEqual(reaction.reactants, ["NH3(g)", "H2O(g)"])

    def testIron(self):
        reactor = self.setupRealReactor()
        reaction = reactor.react(["Fe3O4(s)", "CO(g)"],
                                  K=700)
        self.assertEqual(reaction.products, ['FeO(s)', 'FeO(s)', 'FeO(s)',
                                             'CO2(g)'])
        self.assertEqual(reaction.reactants, ["Fe3O4(s)","CO(g)"])
