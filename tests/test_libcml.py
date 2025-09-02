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
import glob
import os
import unittest
import libcml.Cml as Cml
from libcml import CachedCml
import xml.etree.ElementTree as ET
import xmlschema  # Krävs för schema-validering
from libreact import Reaction as ReactionUtils
from collections import Counter

REACTIONS_SCHEMA_PATH = "data/reactions/reactions.xsd"
LEVELS_SCHEMA_PATH = "data/levels/levels.xsd"
_REACTIONS_SCHEMA = xmlschema.XMLSchema(REACTIONS_SCHEMA_PATH)
_LEVELS_SCHEMA = xmlschema.XMLSchema(LEVELS_SCHEMA_PATH)

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
        self.assertEqual(m.is_atom, False)

    def testParsePropane(self):
        m = Cml.Molecule()
        m.parse("tests/testPropane.cml")
        self.assertEqual(len(m.atoms), 12)
        self.assertEqual(len(m.bonds), 11)
        self.assertEqual(m.atoms["a1"].elementType, "H")
        self.assertEqual(m.atoms["a1"].formalCharge, 0)
        self.assertEqual(m.atoms["a1"].x, -4.719821)
        self.assertEqual(m.atoms["a1"].y, 1.866564)
        self.assertEqual(m.atoms["a1"].z, -1.096199)
        self.assertEqual(m.atoms["a1"].pos, (-4.719821, 1.866564))
        self.assertEqual(m.atoms["a2"].x, -4.299694)
        self.assertEqual(m.atoms["a2"].y, 2.06041)
        self.assertEqual(m.atoms["a2"].z, -2.091249)
        self.assertEqual(m.atoms["a2"].pos, (-4.299694, 2.06041))
        self.assertEqual(m.atoms["a2"].elementType, "C")
        self.assertEqual(m.atoms["a2"].formalCharge, 0)
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
        self.assertEqual(m.states["Gas"].short, "g")
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

    def testWriteAndParsePropertys(self):
        m = Cml.Molecule()
        m.atoms["a1"] = Cml.Atom("a1", "H", 0, 0, 0)
        m.property["Name"] = "Hydrogen"
        m.property["Weight"] = 1.0
        m.property["Radius"] = 25
        m.write("tests/testHydrogen.cml")
        m = Cml.Molecule()
        m.parse("tests/testHydrogen.cml")
        self.assertEqual(m.property["Name"], "Hydrogen")
        self.assertEqual(m.property["Weight"], 1.0)
        self.assertEqual(m.property["Radius"], 25)
        self.assertEqual(m.is_atom, True)
        os.remove("tests/testHydrogen.cml")

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
        m.parse("data/molecule/NaCl.cml")
        self.assertEqual(len(m.atoms), 2)
        self.assertEqual(len(m.bonds), 1)
        self.assertEqual(m.atoms["a1"].elementType, "Na")
        self.assertEqual(m.atoms["a1"].formalCharge, 1)
        self.assertEqual(m.atoms["a1"].x, 1.0)
        self.assertEqual(m.atoms["a1"].y, 0.0)
        self.assertEqual(m.atoms["a2"].x, 0.0)
        self.assertEqual(m.atoms["a2"].y, 0.0)
        self.assertEqual(m.atoms["a2"].elementType, "Cl")
        self.assertEqual(m.atoms["a2"].formalCharge, -1)

    def testParseLevel(self):
        m = Cml.Level()
        m.parse("tests/testlevel.cml")
        expected = ['H+(g)', 'O(g)', 'O(g)', 'H+(g)', 'P(g)', 'F(g)', 'Al(s)']
        self.assertEqual(m.molecules, expected)
        self.assertEqual(m.victory_condition, ["H2O"])
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

    def testParseLevelWithMiningEffect(self):
        m = Cml.Level()
        m.parse("data/levels/12-Iron-1.cml")
        self.assertEqual(m.effects[0].title, "Mining")
        self.assertEqual(m.effects[0].molecules, ['Fe2O3(s)', 'Fe3O4(s)'])


    def testParseLevelWithReactionHint(self):
        level = Cml.Level()
        level.parse("data/levels/42-Life-3-Guanine.cml")
        self.assertEqual(len(level.reactions_hint), 3)
        self.assertEqual(level.reactions_hint[2].reactants, ['C4H6N4O', 'HCN', 'NH3', 'NH3'])
        self.assertEqual(level.reactions_hint[2].products, ['C5H5N5O(s)', 'NH4+(aq)', 'NH4+(aq)'])

    def testAllMolecules(self):
        for filename in glob.glob("data/molecule/*"):
            m = Cml.Molecule()
            try:
                m.parse(filename)
            except Exception as e:
                self.fail("Failed to parse %s: %s" % (filename, e))
            self.assertNotEqual(len(m.states), 0, msg="%s dont have any state info!" % filename)


    def testThatNoDuplicatesExists(self):
        atomMatrix = {}
        for filename in glob.glob("data/molecule/*"):
            m = Cml.Molecule()
            try:
                m.parse(filename)
                if m.is_atom:
                    continue
                atoms_string = ""
                for atom in m.atoms_sorted:
                    atoms_string += atom.elementType + str(atom.formalCharge) + str(atom.x) + str(atom.y) + str(atom.z)
                if atoms_string in atomMatrix:
                    self.fail("Duplicate found: %s and %s" % (atomMatrix[atoms_string], filename))
                atomMatrix[atoms_string] = filename
            except Exception as e:
                self.fail("Failed to parse %s: %s" % (filename, e))

    def test_molecule_filename_formula_matches_atom_array(self):
        """Validate that atomArray matches the molecular formula portion of the filename."""
        errors = []
        for filename in glob.glob("data/molecule/*.cml"):
            m = Cml.Molecule()
            try:
                m.parse(filename)
            except Exception as e:
                errors.append(f"Failed to parse {filename}: {e}")
                continue
            base = os.path.basename(filename)
            if base.endswith('.cml'):
                base = base[:-4]
            # Use substring before first charge sign (+/-) to strip ionic charge notation
            core = base
            for idx, ch in enumerate(base):
                if ch in '+-':
                    core = base[:idx]
                    break
            if not core:  # hoppa över rena joner utan atominfo i namnet (teoretiskt)
                continue
            expected = ReactionUtils.getAtomCount([core])
            actual = Counter(a.elementType for a in m.atoms.values())
            if expected != actual:
                errors.append(f"{filename}: formula counts {dict(expected)} != atomArray counts {dict(actual)}")
        if errors:
            self.fail("\n".join(errors))

    def testReadAndWriteDescription(self):
        m = Cml.Molecule()
        m.property["Description"] = "H20 is the base of all life."
        m.property["Description-Attribution"] = "Wikipedia, CC-BY-SA"
        m.write("tests/testWrite.cml")
        m = Cml.Molecule()
        m.parse("tests/testWrite.cml")
        self.assertEqual(m.property["Description"],  "H20 is the base of all life.")
        self.assertEqual(m.property["Description-Attribution"],  "Wikipedia, CC-BY-SA")
        os.remove("tests/testWrite.cml")

    def test_reactions_files_schema(self):
        """Validate all reaction collection files using pre-installed xmlschema.

        Ingen automatisk installation sker; om xmlschema saknas hoppas testet över.
        """
        schema = _REACTIONS_SCHEMA
        errors = []
        for filename in glob.glob("data/reactions/*.cml"):
            try:
                schema.validate(filename)
            except Exception as e:
                errors.append(f"{filename}: {e}")
        if errors:
            self.fail("\n".join(errors))

    def test_levels_files_schema(self):
        """Validate all level definition files using levels.xsd schema."""
        schema = _LEVELS_SCHEMA
        errors = {}
        for filename in glob.glob("data/levels/*.cml"):
            try:
                schema.validate(filename)
            except Exception as e:
                errors[filename] = str(e)
        if errors:
            joined = "\n".join(f"{k}: {v}" for k,v in errors.items())
            self.fail(joined)


if __name__ == '__main__':
    unittest.main()
