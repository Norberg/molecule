# Molecule - a chemical reaction puzzle game
# Copyright (C) 2014 Simon Norberg <simon@pthread.se>
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
from libreact.MultiMap import MultiMap, MultiMapEntry

class TestMultiMap(unittest.TestCase):
    
    def test_create(self):
        v1 = "Value 1"
        v2 = "Value 2"
        v3 = "Value 3"
        v4 = "Value 4"
        v5 = "Value 5"
        e = list()
        e.append(MultiMapEntry(["A", "B"], v1))
        e.append(MultiMapEntry(["C", "B"], v2))
        e.append(MultiMapEntry(["D", "C"], v3))
        e.append(MultiMapEntry(["E", "F"], v4))
        e.append(MultiMapEntry(["F", "A"], v5))
        m = MultiMap(e)
        self.assertEqual(m["A"], [v1,v5])
        self.assertEqual(m["B"], [v1,v2])
        self.assertEqual(m["C"], [v2, v3])
        self.assertEqual(m["D"], [v3])
        self.assertEqual(m["E"], [v4])
        self.assertEqual(m["F"], [v4, v5])

    def test_entryMapper(self):
        class OrigData:
            def __init__(self, k, v):
                self.k = k
                self.v = v

        class EntryMapper:
            def __init__(self, origData):
                self.keys = origData.k
                self.value = origData.v

        orig_list = [OrigData(["A", "B"],6), OrigData(["A", "C"], 10)]
        m = MultiMap(orig_list, EntryMapper)
        self.assertEqual(m["A"], [6, 10])
        self.assertEqual(m["B"], [6])
        self.assertEqual(m["C"], [10])

