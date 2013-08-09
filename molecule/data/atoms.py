from molecule.Molecule import Molecule
import molecule.State as State

atom_layouts = dict()

def add_atom(symbol, states, mass):
	m = Molecule(symbol, states, mass)
	global atom_layouts
	atom_layouts[symbol] = m
		
	
s = State.Gas(249, -11)
add_atom("O", [s], 16)

s = State.Gas(218, 114)
add_atom("H", [s], 1)

s = list()
s.append(State.Gas(1536, 1517))
s.append(State.Aqueous(0, 0))
add_atom("H+", s, 1)

s = list()
s.append(State.Solid(0, 32)) #rhombic
s.append(State.Gas(277, 168))
add_atom("S", s, 32)

s = list()
s.append(State.Aqueous(42, 22))
add_atom("S-2", s, 32)

s = list()
s.append(State.Solid(0, 51))
s.append(State.Gas(107, 154))
add_atom("Na", s, 23)

s = list()
s.append(State.Aqueous(-240, 59))
s.append(State.Gas(609, 148))
add_atom("Na+", s, 23)

s = list()
s.append(State.Solid(0, 28))
add_atom("Al", s, 27)

s = list()
s.append(State.Solid(0, 42))
s.append(State.Gas(178, 155))
add_atom("Ca", s, 40) 

s = list()
s.append(State.Aqueous(-543, -53))
s.append(State.Gas(1926, None))
add_atom("Ca+2", s, 40) 

s = list()
s.append(State.Solid(0, 6)) #graphite
s.append(State.Gas(717, 158))
add_atom("C", s, 12)

s = list()
s.append(State.Gas(121, 165))
add_atom("Cl", s, 35)

s = list()
s.append(State.Aqueous(-167, 56))
s.append(State.Gas(-234, 153))
add_atom("Cl-", s, 35)

s = list()
s.append(State.Gas(79, 159))
add_atom("F", s, 19)

s = list()
s.append(State.Gas(473, 153))
add_atom("N", s, 14)

s = list()
s.append(State.Solid(0, 41)) #white
s.append(State.Gas(316, 163))
add_atom("P", s, 31)

s = list()
s.append(State.Solid(0, 33))
s.append(State.Gas(338, 166))
add_atom("Cu", s, 63)

s = list()
s.append(State.Aqueous(72, 41))
add_atom("Cu+", s, 63)

s = list()
s.append(State.Aqueous(65, -100))
add_atom("Cu+2", s, 63)
