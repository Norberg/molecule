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

if __name__ == '__main__':
	unittest.main()	
