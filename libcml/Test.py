import unittest
import Cml

class TestCML(unittest.TestCase):

	def testParseAmmonia(self):
		m = Cml.Molecule()
		m.parse("testAmmonia.cml")
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
		m.parse("testPropane.cml")
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
		m.parse("testPropane.cml")
		m.write("testWrite.cml")
		m = Cml.Molecule()
		m.parse("testWrite.cml")
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
	
	def testSortedAtoms(self):
		m = Cml.Molecule()
		m.parse("testPropane.cml")
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
		m.parse("testPropane.cml")
		self.assertEqual(m.max_pos(), (-0.605318, 3.557669, -1.096199))
		self.assertEqual(m.min_pos(), (-4.928943, 1.137126, -4.097433))
		m.normalize_pos()
		self.assertEqual(m.max_pos(), (4.323625, 3.557669, 3.0012339999999997))
		self.assertEqual(m.min_pos(), (0.0, 1.137126, 0.0))
		self.assertEqual(len(m.atoms), 12)
		self.assertEqual(len(m.bonds), 11)
		self.assertEqual(m.atoms["a1"].elementType, "H")
		self.assertAlmostEqual(m.atoms["a1"].x, 0.209122)
		self.assertAlmostEqual(m.atoms["a1"].y, 1.866564)
		self.assertAlmostEqual(m.atoms["a1"].z, 3.001234)
		self.assertAlmostEqual(m.atoms["a2"].x, 0.629249)
		self.assertAlmostEqual(m.atoms["a2"].y, 2.06041)
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
		m.write("testOxygen.cml")
		m = Cml.Molecule()
		m.parse("testOxygen.cml")
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
	
	def testParseStatePropertys(self):
		m = Cml.Molecule()
		m.parse("testProperty.cml")
		self.assertEqual(m.states["Gas"].enthalpy, -426)
		self.assertEqual(m.states["Gas"].entropy, 64)
		self.assertEqual(m.states["Aqueous"].ions, ["Na+", "OH-"])

	def testWriteAndParseStatePropertys(self):
		m = Cml.Molecule()
		gas = Cml.State("Gas", -426, 64)
		aq = Cml.State("Aqueous", ions=["Na+", "OH-"])
		m.states["Gas"] = gas
		m.states["Aqueous"] = aq
		m.write("testSodiumhydroxide.cml")
		m = Cml.Molecule()
		m.parse("testSodiumhydroxide.cml")
		self.assertEqual(m.states["Gas"].enthalpy, -426)
		self.assertEqual(m.states["Gas"].entropy, 64)
		self.assertEqual(m.states["Aqueous"].ions, ["Na+", "OH-"])
		
		
if __name__ == '__main__':
	unittest.main()	
