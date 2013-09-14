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
import os
import unittest
import libcml.Cml as Cml
from libcml import CachedCml

class TestCML(unittest.TestCase):

	def testParseAmmonia(self):
		m = Cml.Molecule()
		m.parse("tests/testAmmonia.cml")
		self.assertEqual(len(m.atoms), 4)
		self.assertEqual(len(m.bonds), 3)
		self.assertEqual(m.atoms["a1"].elementType, "N")
		self.assertEqual(m.atoms["a1"].x, 1.0)
		self.assertEqual(m.atoms["a1"].y, 0.0)
		self.assertEqual(m.atoms["a2"].x, 2.02)
		self.assertEqual(m.atoms["a2"].y, 0.0)
		self.assertEqual(m.atoms["a2"].elementType, "H")
		self.assertEqual(m.bonds[0].atomA.id, "a1")
		self.assertEqual(m.bonds[0].atomB.id, "a2")
		
	def testParsePropane(self):
		m = Cml.Molecule()
		m.parse("tests/testPropane.cml")
		self.assertEqual(len(m.atoms), 12)
		self.assertEqual(len(m.bonds), 11)
		self.assertEqual(m.atoms["a1"].elementType, "H")
		self.assertEqual(m.atoms["a1"].x, -4.719821)
		self.assertEqual(m.atoms["a1"].y, 1.866564)
		self.assertEqual(m.atoms["a1"].z, -1.096199)
		self.assertEqual(m.atoms["a1"].pos, (-4.719821, 1.866564))
		self.assertEqual(m.atoms["a2"].x, -4.299694)
		self.assertEqual(m.atoms["a2"].y, 2.06041)
		self.assertEqual(m.atoms["a2"].z, -2.091249)
		self.assertEqual(m.atoms["a2"].pos, (-4.299694, 2.06041))
		self.assertEqual(m.atoms["a2"].elementType, "C")
		self.assertEqual(m.bonds[0].atomA.id, "a1")
		self.assertEqual(m.bonds[0].atomB.id, "a2")
		self.assertAlmostEqual(m.bonds[0].atomA.x, -4.719821)
		self.assertAlmostEqual(m.bonds[0].atomA.y, 1.866564)
		self.assertAlmostEqual(m.bonds[0].atomA.z, -1.096199)
		self.assertAlmostEqual(m.bonds[0].atomB.x, -4.299694)
		self.assertAlmostEqual(m.bonds[0].atomB.y, 2.06041)
		self.assertAlmostEqual(m.bonds[0].atomB.z, -2.091249) 
	
	def testWriteAndParseAgain(self):
		m = Cml.Molecule()
		m.parse("tests/testPropane.cml")
		m.write("tests/testWrite.cml")
		m = Cml.Molecule()
		m.parse("tests/testWrite.cml")
		self.assertEqual(len(m.atoms), 12)
		self.assertEqual(len(m.bonds), 11)
		self.assertEqual(m.atoms["a1"].elementType, "H")
		self.assertAlmostEqual(m.atoms["a1"].x, -4.719821)
		self.assertAlmostEqual(m.atoms["a1"].y, 1.866564)
		self.assertAlmostEqual(m.atoms["a1"].z, -1.096199)
		self.assertAlmostEqual(m.atoms["a2"].x, -4.299694)
		self.assertAlmostEqual(m.atoms["a2"].y, 2.06041)
		self.assertAlmostEqual(m.atoms["a2"].z, -2.091249)
		self.assertEqual(m.atoms["a2"].elementType, "C")
		self.assertEqual(m.bonds[0].atomA.id, "a1")
		self.assertEqual(m.bonds[0].atomB.id, "a2")
		os.remove("tests/testWrite.cml")
	
	def testSortedAtoms(self):
		m = Cml.Molecule()
		m.parse("tests/testPropane.cml")
		self.assertEqual(m.atoms_sorted[0].id, "a1")
		self.assertEqual(m.atoms_sorted[1].id, "a2")
		self.assertEqual(m.atoms_sorted[2].id, "a3")
		self.assertEqual(m.atoms_sorted[3].id, "a4")
		self.assertEqual(m.atoms_sorted[4].id, "a5")
		self.assertEqual(m.atoms_sorted[5].id, "a6")
		self.assertEqual(m.atoms_sorted[6].id, "a7")
		self.assertEqual(m.atoms_sorted[7].id, "a8")
		self.assertEqual(m.atoms_sorted[8].id, "a9")
		self.assertEqual(m.atoms_sorted[9].id, "a10")
		self.assertEqual(m.atoms_sorted[10].id, "a11")
		self.assertEqual(m.atoms_sorted[11].id, "a12")
		self.assertEqual(m.getDigits("asdas23434"), 23434)
	
	def testNormalizePos(self):
		m = Cml.Molecule()
		m.parse("tests/testPropane.cml")
		self.assertEqual(m.max_pos(), (-0.605318, 3.557669, -1.096199))
		self.assertEqual(m.min_pos(), (-4.928943, 1.137126, -4.097433))
		m.normalize_pos()
		self.assertEqual(m.max_pos(), (4.323625, 2.4205430000000003, 3.0012339999999997))
		self.assertEqual(m.min_pos(), (0.0, 0.0, 0.0))
		self.assertEqual(len(m.atoms), 12)
		self.assertEqual(len(m.bonds), 11)
		self.assertEqual(m.atoms["a1"].elementType, "H")
		self.assertAlmostEqual(m.atoms["a1"].x, 0.209122)
		self.assertAlmostEqual(m.atoms["a1"].y, 0.729438)
		self.assertAlmostEqual(m.atoms["a1"].z, 3.001234)
		self.assertAlmostEqual(m.atoms["a2"].x, 0.629249)
		self.assertAlmostEqual(m.atoms["a2"].y, 0.923284)
		self.assertAlmostEqual(m.atoms["a2"].z, 2.006184)
		self.assertEqual(m.atoms["a2"].elementType, "C")
		self.assertEqual(m.bonds[0].atomA.id, "a1")
		self.assertEqual(m.bonds[0].atomB.id, "a2")
	
	def testCreateMoleculeWithCharge(self):
		m = Cml.Molecule()
		a1 = Cml.Atom("a1", "C",-1, 0, 0)
		a2 = Cml.Atom("a2", "O", 1, 1, 0)
		m.atoms["a1"] = a1
		m.atoms["a2"] = a2
		b = Cml.Bond(a1, a2, 2)
		m.bonds.append(b)
		m.write("tests/testOxygen.cml")
		m = Cml.Molecule()
		m.parse("tests/testOxygen.cml")
		self.assertAlmostEqual(m.atoms["a1"].x, 0.0)
		self.assertAlmostEqual(m.atoms["a1"].y, 0.0)	
		self.assertEqual(m.atoms["a1"].elementType, "C")
		self.assertEqual(m.atoms["a1"].formalCharge,-1)
		self.assertAlmostEqual(m.atoms["a2"].x, 1.0)
		self.assertAlmostEqual(m.atoms["a2"].y, 0.0)	
		self.assertEqual(m.atoms["a2"].elementType, "O")
		self.assertEqual(m.atoms["a2"].formalCharge,1)
		self.assertEqual(m.bonds[0].atomA.id, "a1")
		self.assertEqual(m.bonds[0].atomB.id, "a2")
		self.assertEqual(m.bonds[0].bonds, 2)
		os.remove("tests/testOxygen.cml")
	
	def testParseStatePropertys(self):
		m = Cml.Molecule()
		m.parse("tests/testProperty.cml")
		self.assertEqual(m.states["Gas"].enthalpy, -426)
		self.assertEqual(m.states["Gas"].entropy, 64)
		self.assertEqual(m.get_state("g").entropy, 64)
		self.assertEqual(m.get_state("l"), None)
		self.assertEqual(m.states["Aqueous"].ions, ["Na+", "OH-"])

	def testWriteAndParseStatePropertys(self):
		m = Cml.Molecule()
		gas = Cml.State("Gas", -426, 64)
		aq = Cml.State("Aqueous", ions=["Na+", "OH-"])
		m.states["Gas"] = gas
		m.states["Aqueous"] = aq
		m.write("tests/testSodiumhydroxide.cml")
		m = Cml.Molecule()
		m.parse("tests/testSodiumhydroxide.cml")
		self.assertEqual(m.states["Gas"].enthalpy, -426)
		self.assertEqual(m.states["Gas"].entropy, 64)
		self.assertEqual(m.states["Aqueous"].ions, ["Na+", "OH-"])
		self.assertEqual(m.states["Aqueous"].ions_str, "Na+,OH-")
		os.remove("tests/testSodiumhydroxide.cml")

	def testParseReactions(self):
		r = Cml.Reactions()
		r.parse("tests/reactions.cml")
		self.assertEqual(r.reactions[0].reactants, ["H2","O"])
		self.assertEqual(r.reactions[0].products, ["H2O(s)"])
		self.assertEqual(r.reactions[1].reactants, ['SO3', 'H2O'])
		self.assertEqual(r.reactions[1].products, ["H2SO4(aq)"])

	def testWriteAndParseReactions(self):
		r = Cml.Reactions()
		r1 = Cml.Reaction(["O", "O"], ["O2"])
		r.reactions.append(r1)
		r2 = Cml.Reaction(["H+", "H+"], ["H2"])
		r.reactions.append(r2)
		r.write("tests/writtenReactions.cml")
		r = Cml.Reactions()
		r.parse("tests/writtenReactions.cml")
		self.assertEqual(r.reactions[0].reactants, ["O","O"])
		self.assertEqual(r.reactions[0].products, ["O2"])
		self.assertEqual(r.reactions[1].reactants, ['H+', 'H+'])
		self.assertEqual(r.reactions[1].products, ["H2"])
		os.remove("tests/writtenReactions.cml")


	def testCachedMolecule(self):
		m = Cml.Molecule()
		m.parse("tests/testPropane.cml")
		m.write("tests/testWrite.cml")
		c = CachedCml.getMoleculeCml("tests/testWrite.cml")
		self.assertEqual(len(m.atoms), 12)
		self.assertEqual(len(m.bonds), 11)
		self.assertEqual(m.atoms["a1"].elementType, "H")
		self.assertAlmostEqual(m.atoms["a1"].x, -4.719821)
		self.assertAlmostEqual(m.atoms["a1"].y, 1.866564)
		self.assertAlmostEqual(m.atoms["a1"].z, -1.096199)
		self.assertAlmostEqual(m.atoms["a2"].x, -4.299694)
		self.assertAlmostEqual(m.atoms["a2"].y, 2.06041)
		self.assertAlmostEqual(m.atoms["a2"].z, -2.091249)
		self.assertEqual(m.atoms["a2"].elementType, "C")
		self.assertEqual(m.bonds[0].atomA.id, "a1")
		self.assertEqual(m.bonds[0].atomB.id, "a2")
		os.remove("tests/testWrite.cml")
		c = CachedCml.getMoleculeCml("tests/testWrite.cml")
		self.assertEqual(len(m.atoms), 12)
		self.assertEqual(len(m.bonds), 11)
		self.assertEqual(m.atoms["a1"].elementType, "H")
		self.assertAlmostEqual(m.atoms["a1"].x, -4.719821)
		self.assertAlmostEqual(m.atoms["a1"].y, 1.866564)
		self.assertAlmostEqual(m.atoms["a1"].z, -1.096199)
		self.assertAlmostEqual(m.atoms["a2"].x, -4.299694)
		self.assertAlmostEqual(m.atoms["a2"].y, 2.06041)
		self.assertAlmostEqual(m.atoms["a2"].z, -2.091249)
		self.assertEqual(m.atoms["a2"].elementType, "C")
		self.assertEqual(m.bonds[0].atomA.id, "a1")
		self.assertEqual(m.bonds[0].atomB.id, "a2")
		
	def testParseMoleculeWithoutBonds(self):
		m = Cml.Molecule()
		m.parse("data/molecule/AgCl.cml")
		self.assertEqual(len(m.atoms), 2)
		self.assertEqual(len(m.bonds), 0)
		self.assertEqual(m.atoms["a1"].elementType, "Cl")
		self.assertEqual(m.atoms["a1"].formalCharge, -1)
		self.assertEqual(m.atoms["a1"].x, 1.0)
		self.assertEqual(m.atoms["a1"].y, 0.0)
		self.assertEqual(m.atoms["a2"].x, 0.0)
		self.assertEqual(m.atoms["a2"].y, 0.0)
		self.assertEqual(m.atoms["a2"].elementType, "Ag")
		self.assertEqual(m.atoms["a2"].formalCharge, 1)

	def testParseLevel(self):
		m = Cml.Level()
		m.parse("tests/testlevel.cml")
		expected = ['H+(g)', 'O(g)', 'O(g)', 'H+(g)', 'P(g)', 'F(g)', 'Al(s)']
		self.assertEqual(m.molecules, expected)
		self.assertEqual(m.victory_condition, ["H2O(aq)"])
		self.assertEqual(m.objective, "Create a water molecule")
		self.assertEqual(m.hint, "H + H + O => H2O")
		self.assertEqual(m.effects[0].title, "Fire")
		self.assertEqual(m.effects[0].value, 800)
		self.assertEqual(m.effects[0].x2, 12)
		self.assertEqual(m.effects[0].y2, 10)

	def testParseLevel01(self):
		m = Cml.Level()
		m.parse("data/levels/01-Water.cml")
		expected = ['H+(g)', 'O(g)', 'O(g)', 'H+(g)', 'P(g)', 'F(g)', 'Al(s)']
		self.assertEqual(m.molecules, expected)
		self.assertEqual(m.victory_condition, ["H2O"])
		self.assertEqual(m.objective, "Create a water molecule")
		self.assertEqual(m.hint, "H + H + O => H2O")

if __name__ == '__main__':
	unittest.main()	
