from molecule.Molecule import Molecule
import molecule.State as State

molecule_layouts = dict()

def add_molecule_layout(molecule):
	global molecule_layouts
	molecule_layouts[molecule.formula] = molecule
		
#Calcium (Ca)
s = list()
s.append(State.Solid(-986,83))	
s.append(State.Aqueous(ions=["Ca+2"] + 2*["OH-"]))	
m = Molecule("CaO2H2", s) 
add_molecule_layout(m)

s = list()
s.append(State.Solid(-1207,93))	
m = Molecule("CaCO3", s)
add_molecule_layout(m)

#Carbon(C)
s = list()
s.append(State.Gas(-119, 197))	
m = Molecule("CO", s)
add_molecule_layout(m)

s = list()
s.append(State.Gas(-394, 214))	
m = Molecule("CO2", s)
add_molecule_layout(m)

s = list()
s.append(State.Aqueous(-677, -57))	
m = Molecule("CO3-2", s)
add_molecule_layout(m)

s = list()
s.append(State.Gas(-75, 186))	
m = Molecule("CH4", s)
add_molecule_layout(m)

s = list()
s.append(State.Aqueous(-319, 174)) #TODO, aqueues -> solid?
s.append(State.Solid(-319, 174)) #TODO, aqueues -> solid?
m = Molecule("CH4N2O", s)
add_molecule_layout(m)

s = list()
s.append(State.Aqueous(-278, 161)) #TODO, aqueues -> solid?
m = Molecule("C2H6O", s)
add_molecule_layout(m)

#Chlorine (Cl)
s = list()
s.append(State.Aqueous(-92, 187))	
s.append(State.Gas(-92, 187))	
m = Molecule("HCl", s)
add_molecule_layout(m)

#Copper (Cu)
s = list()
s.append(State.Solid(None, None)) #unknown	
s.append(State.Aqueous(ions=["Cu+2"] +["SO4-2"]))	
m = Molecule("CuSO4", s)
add_molecule_layout(m)

#Hydrogen(H)
s = list()
s.append(State.Gas(0, 131))	
m = Molecule("H2", s)
add_molecule_layout(m)

s = list()
s.append(State.Liquid(-286, 70))	
s.append(State.Gas(-242, 189))
m = Molecule("H2O", s)
add_molecule_layout(m)

#Nitrogen (N)
s = list()
s.append(State.Gas(0, 192))	
m = Molecule("N2", s) 
add_molecule_layout(m)

s = list()
s.append(State.Gas(-46, 193))	
s.append(State.Aqueous(-80, 111))	
m = Molecule("NH3", s)
add_molecule_layout(m)

s = list()
s.append(State.Aqueous(-132, 113))	
m = Molecule("NH4+", s)
add_molecule_layout(m)

#Oxygen(O)
s = list()
s.append(State.Gas(0, 205))	
m = Molecule("O2", s)
add_molecule_layout(m)

s = list()
s.append(State.Aqueous(-230, -11))
m = Molecule("OH-", s) 
add_molecule_layout(m)
	
# Phosphorus (P)
s = list()
s.append(State.Gas(59, 280))	
m = Molecule("P4", s)
add_molecule_layout(m)

s = list()
s.append(State.Aqueous(-1277, -222))	
m = Molecule("PO4-3", s)
add_molecule_layout(m)

#Sodium (Na)
s = list()
s.append(State.Solid(-411, 72))	
m = Molecule("NaCl", s)
add_molecule_layout(m)

s = list()
s.append(State.Solid(-1387, 150))	
m = Molecule("Na2SO4", s)
add_molecule_layout(m)

s = list()
s.append(State.Solid(-426, 64))	
s.append(State.Aqueous(ions=["Na+", "OH-"]))	
m = Molecule("NaOH", s)
add_molecule_layout(m)

s = list()
s.append(State.Solid(-1131, 139))	
s.append(State.Aqueous(ions=2*["Na+"] + ["CO3-2"]))	
m = Molecule("Na2CO3", s)
add_molecule_layout(m)

s = list()
s.append(State.Solid(None, None)) #unknown	
s.append(State.Aqueous(ions=3*["Na+"] + ["PO4-3"]))	
m = Molecule("Na3PO4", s)
add_molecule_layout(m)

#Sulphur (S)
s = list()
s.append(State.Gas(-396, 257))	
m = Molecule("SO3", s)
add_molecule_layout(m)

s = list()
s.append(State.Aqueous(-909, 20))	
m = Molecule("SO4-2", s)
add_molecule_layout(m)

s = list()
s.append(State.Aqueous(-814, 157))	
m = Molecule("H2SO4", s)
add_molecule_layout(m)
