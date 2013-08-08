import unittest
import Cml

class TestCML(unittest.TestCase):

	def testParseAmmonia(self):
		m = Cml.Molecule()
		m.parse("testAmmonia.cml")
		m.printer()
		self.assertEqual(len(m.atoms), 4)
		self.assertEqual(len(m.bonds), 3)
		self.assertEqual(m.atoms["a1"].elementType, "N")
		self.assertEqual(m.atoms["a1"].x, 1.0)
		self.assertEqual(m.atoms["a1"].y, 0.0)
		self.assertEqual(m.atoms["a2"].x, 2.02)
		self.assertEqual(m.atoms["a2"].y, 0.0)
		self.assertEqual(m.atoms["a2"].elementType, "H")
		self.assertEqual(m.bonds[0].atomA, "a1")
		self.assertEqual(m.bonds[0].atomB, "a2")
		
	def testParsePropane(self):
		m = Cml.Molecule()
		m.parse("testPropane.cml")
		m.printer()
		self.assertEqual(len(m.atoms), 12)
		self.assertEqual(len(m.bonds), 11)
		self.assertEqual(m.atoms["a1"].elementType, "H")
		self.assertEqual(m.atoms["a1"].x, -4.719821)
		self.assertEqual(m.atoms["a1"].y, 1.866564)
		self.assertEqual(m.atoms["a1"].z, -1.096199)
		self.assertEqual(m.atoms["a2"].x, -4.299694)
		self.assertEqual(m.atoms["a2"].y, 2.06041)
		self.assertEqual(m.atoms["a2"].elementType, "C")
		self.assertEqual(m.bonds[0].atomA, "a1")
		self.assertEqual(m.bonds[0].atomB, "a2")
	
	def testWriteAndParseAgain(self):
		m = Cml.Molecule()
		m.parse("testPropane.cml")
		m.write("testWrite.cml")
		m = Cml.Molecule()
		m.parse("testWrite.cml")
		m.printer()
		self.assertEqual(len(m.atoms), 12)
		self.assertEqual(len(m.bonds), 11)
		self.assertEqual(m.atoms["a1"].elementType, "H")
		self.assertEqual(m.atoms["a1"].x, -4.719821)
		self.assertEqual(m.atoms["a1"].y, 1.866564)
		self.assertEqual(m.atoms["a1"].z, -1.096199)
		self.assertEqual(m.atoms["a2"].x, -4.299694)
		self.assertEqual(m.atoms["a2"].y, 2.06041)
		self.assertEqual(m.atoms["a2"].elementType, "C")
		self.assertEqual(m.bonds[0].atomA, "a1")
		self.assertEqual(m.bonds[0].atomB, "a2")
	
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
		
if __name__ == '__main__':
	unittest.main()	
