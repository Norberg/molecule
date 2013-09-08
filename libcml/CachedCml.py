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
import Cml
__cml_cache = dict()

def getMolecule(element):
	filename = "data/molecule/%s.cml" % element
	return getMoleculeCml(filename)

def getMoleculeCml(filename):
	global __cml_cache
	if __cml_cache.has_key(filename):
		return __cml_cache[filename]
	
	m = Cml.Molecule()
	m.parse(filename)
	__cml_cache[filename] = m
	return m
				
