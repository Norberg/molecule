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

from molecule import Gui

class TestGui(unittest.TestCase):
    def test_formula_to_html(self):
        self.assertEqual(Gui.formula_to_html("H2O"), "H<sub>2</sub>O")
        self.assertEqual(Gui.formula_to_html("H2SO4"), "H<sub>2</sub>SO<sub>4</sub>")
        self.assertEqual(Gui.formula_to_html("H2O2"), "H<sub>2</sub>O<sub>2</sub>")
        self.assertEqual(Gui.formula_to_html("H+"), "H<sup>+</sup>")
        self.assertEqual(Gui.formula_to_html("H-"), "H<sup>-</sup>")
        self.assertEqual(Gui.formula_to_html("H3O+"), "H<sub>3</sub>O<sup>+</sup>")
        self.assertEqual(Gui.formula_to_html("Ca+2"), "Ca<sup>2+</sup>")
        self.assertEqual(Gui.formula_to_html("HSO4-"), "HSO<sub>4</sub><sup>-</sup>")

    def test_find_and_convert_formulas(self):
        self.assertEqual(Gui.find_and_convert_formulas("The H2O is life"), "The H<sub>2</sub>O is life")
        self.assertEqual(Gui.find_and_convert_formulas("The H2SO4 Is an acid and Ca+2 is an ion"), "The H<sub>2</sub>SO<sub>4</sub> Is an acid and Ca<sup>2+</sup> is an ion")
        self.assertEqual(Gui.find_and_convert_formulas("The 5 in 5H2O is not subscripted"), "The 5 in 5H<sub>2</sub>O is not subscripted")
        self.assertEqual(Gui.find_and_convert_formulas("The OH- is an ion"), "The OH<sup>-</sup> is an ion")
        #TODO: Last - should have been converted to <sup>-</sup>
        self.assertEqual(Gui.find_and_convert_formulas("HSO-4 is another currently not support form to write HSO4-"), "HSO<sup>4-</sup> is another currently not support form to write HSO<sub>4</sub>-")