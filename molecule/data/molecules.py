from molecule.Molecule import Molecule
import molecule.State as State

molecule_layouts = dict()

def add_molecule_layout(molecule):
	if len(molecule.bond_layout) == 0:
		molecule.autoBonds()
	global molecule_layouts
	molecule_layouts[molecule.formula] = molecule
		
#Calcium (Ca)
s = list()
s.append(State.Solid(-986,83))	
s.append(State.Aqueous(ions=["Ca+2"] + 2*["OH-"]))	
m = Molecule("CaO2H2", s) 
m.addAtoms([[' ',' ','Ca',' ',' '],
            ['H','O',' ', 'O','H']])
m.autoBonds()
m.addBond((2,2), (3,1))
m.addBond((4,2), (3,1))
add_molecule_layout(m)

s = list()
s.append(State.Solid(-1207,93))	
m = Molecule("CaCO3", s)
m.addAtoms([['Ca','O',' '],
            ['O', 'C',' '],
            [' ', ' ','O']])
m.addBond((1,1), (2,1))
m.addBond((1,1), (1,2))
m.addBond((1,2), (2,2))
m.addBond((2,1), (2,2))
m.addBond((3,3), (2,2), 2)
add_molecule_layout(m)

#Carbon(C)
s = list()
s.append(State.Gas(-119, 197))	
m = Molecule("CO", s)
m.addAtoms([['C','O']])
m.addBond((1,1),(2,1),3)
add_molecule_layout(m)

s = list()
s.append(State.Gas(-394, 214))	
m = Molecule("CO2", s)
m.addAtoms([['O','C','O']])
m.addBond((1,1),(2,1),2)
m.addBond((2,1),(3,1),2)
add_molecule_layout(m)

s = list()
s.append(State.Aqueous(-677, -57))	
m = Molecule("CO3-2", s)
m.addAtoms([[' ', 'O', ' '],
            [' ', 'C', ' '],
            ['O-',' ','O-']])
m.addBond((2,1),(2,2),2)
m.addBond((2,2),(1,3))
m.addBond((2,2),(3,3))
add_molecule_layout(m)

s = list()
s.append(State.Gas(-75, 186))	
m = Molecule("CH4", s)
m.addAtoms([[' ','H',' '],
            ['H','C','H'],
            [' ','H',' ']])
add_molecule_layout(m)

s = list()
s.append(State.Aqueous(-319, 174)) #TODO, aqueues -> solid?
s.append(State.Solid(-319, 174)) #TODO, aqueues -> solid?
m = Molecule("CH4N2O", s)
m.addAtoms([[' ',' ','O',' ',' '],
            [' ',' ','C',' ',' '],
            ['H','N',' ','N','N'],
            [' ','H',' ','H',' ']])
m.autoBonds()
m.addBond((3,1), (3,2),2)
m.addBond((3,2),(2,3))
m.addBond((3,2),(4,3))
add_molecule_layout(m)

s = list()
s.append(State.Aqueous(-278, 161)) #TODO, aqueues -> solid?
m = Molecule("C2H6O", s)
m.addAtoms([[' ','H','H',' ','H'],
            ['H','C','C','O',' '],
            [' ','H','H',' ',' ']])
m.addBond((2,1),(2,2))
m.addBond((3,1),(3,2))
m.addBond((5,1),(4,2))
m.addBond((1,2),(2,2))
m.addBond((2,2),(3,2))
m.addBond((3,2),(4,2))
m.addBond((2,2),(2,3))
m.addBond((3,2),(3,3))
add_molecule_layout(m)

#Chlorine (Cl)
s = list()
s.append(State.Aqueous(-92, 187))	
s.append(State.Gas(-92, 187))	
m = Molecule("HCl", s)
m.addAtoms([['H','Cl']])
add_molecule_layout(m)

#Copper (Cu)
s = list()
s.append(State.Solid(None, None)) #unknown	
s.append(State.Aqueous(ions=["Cu+2"] +["SO4-2"]))	
m = Molecule("CuSO4", s)
m.addAtoms([[' ',   'O', ' '],
            ['O-',  'S', 'O'],
            ['Cu+2','O-',' ']])
m.addBond((2,2),(2,1), 2)
m.addBond((2,2),(3,2), 2)
m.addBond((2,2),(1,2))
m.addBond((2,2),(3,2))
add_molecule_layout(m)

#Hydrogen(H)
s = list()
s.append(State.Gas(0, 131))	
m = Molecule("H2", s)
m.addAtoms([['H','H']])
add_molecule_layout(m)

s = list()
s.append(State.Liquid(-286, 70))	
s.append(State.Gas(-242, 189))
m = Molecule("H2O", s)
m.addAtoms([['H','O','H']])
add_molecule_layout(m)

#Nitrogen (N)
s = list()
s.append(State.Gas(0, 192))	
m = Molecule("N2", s) 
m.addAtoms([['N','N']])
m.addBond((1,1),(2,1),3)
add_molecule_layout(m)

s = list()
s.append(State.Gas(-46, 193))	
s.append(State.Aqueous(-80, 111))	
m = Molecule("NH3", s)
m.addAtoms([['H',' ','H'],
            [' ','N',' '],
            [' ','H',' ']])
m.addBond((1,1),(2,2))
m.addBond((3,1),(2,2))
m.addBond((2,3),(2,2))
add_molecule_layout(m)

s = list()
s.append(State.Aqueous(-132, 113))	
m = Molecule("NH4+", s)
m.addAtoms([[' ','H' ,' '],
            ['H','N+','H'],
            [' ','H' ,' ']])
add_molecule_layout(m)

#Oxygen(O)
s = list()
s.append(State.Gas(0, 205))	
m = Molecule("O2", s)
m.addAtoms([['O','O']])
m.addBond((1,1),(2,1),2)
add_molecule_layout(m)

s = list()
s.append(State.Aqueous(-230, -11))
m = Molecule("OH-", s) 
m.addAtoms([['O','H-']])
add_molecule_layout(m)
	
# Phosphorus (P)
s = list()
s.append(State.Gas(59, 280))	
m = Molecule("P4", s)
m.addAtoms([[' ','P',' ','P'],
            ['P',' ','P',' ']])
m.addBond((1,2),(2,1),3)
m.addBond((2,1),(3,2),2)
m.addBond((3,2),(4,1),3)
add_molecule_layout(m)

s = list()
s.append(State.Aqueous(-1277, -222))	
m = Molecule("PO4-3", s)
m.addAtoms([[' ' ,'O' ,' '],
            ['O-','P' ,'O-'],
            [' ' ,'O-',' ']])
add_molecule_layout(m)

#Sodium (Na)
s = list()
s.append(State.Solid(-411, 72))	
m = Molecule("NaCl", s)
m.addAtoms([['Na','Cl']])
add_molecule_layout(m)

s = list()
s.append(State.Solid(-1387, 150))	
m = Molecule("Na2SO4", s)
m.addAtoms([[' ', 'O', ' ','Na'],
            ['O', 'S+','O',' '],
            [' ', 'O', ' ',' '],
            ['Na',' ', ' ',' ']])
m.autoBonds()
m.addBond((2,1),(2,2),2)
m.addBond((1,2),(2,2),2)
m.addBond((1,4),(2,3))
m.addBond((4,1),(3,2))
add_molecule_layout(m)

s = list()
s.append(State.Solid(-426, 64))	
s.append(State.Aqueous(ions=["Na+", "OH-"]))	
m = Molecule("NaOH", s)
m.addAtoms([['Na','O','H']])
add_molecule_layout(m)

s = list()
s.append(State.Solid(-1131, 139))	
s.append(State.Aqueous(ions=2*["Na+"] + ["CO3-2"]))	
m = Molecule("Na2CO3", s)
m.addAtoms([[' ', 'O',' ','O',' '],
            ['Na',' ','C',' ','Na'],
            [' ', ' ','O',' ',' ']])
m.autoBonds()
m.addBond((1,2), (2,1))
m.addBond((2,1), (3,2))
m.addBond((3,2), (3,3),2)
m.addBond((3,2), (4,1))
m.addBond((4,1), (5,2))
add_molecule_layout(m)

s = list()
s.append(State.Solid(None, None)) #unknown	
s.append(State.Aqueous(ions=3*["Na+"] + ["PO4-3"]))	
m = Molecule("Na3PO4", s)
m.addAtoms([[' ', ' ','O', ' ',' '],
            ['Na','O','P', 'O','Na'],
            [' ', ' ','O', ' ',' '],
            [' ', ' ','Na',' ',' ']])
m.autoBonds()
m.addBond((3,1),(3,2),2)
add_molecule_layout(m)

#Sulphur (S)
s = list()
s.append(State.Gas(-396, 257))	
m = Molecule("SO3", s)
m.addAtoms([['O',' ','O'],
            [' ','S',' '],
            [' ','O',' ']])
m.addBond((1,1),(2,2),2)
m.addBond((3,1),(2,2),2)
m.addBond((2,3),(2,2),2)
add_molecule_layout(m)

s = list()
s.append(State.Aqueous(-909, 20))	
m = Molecule("SO4-2", s)
m.addAtoms([[' ','O' ,' '],
            ['O','S-2','O'],
            [' ','O' ,' ']])
add_molecule_layout(m)

s = list()
s.append(State.Aqueous(-814, 157))	
m = Molecule("H2SO4", s)
m.addAtoms([[' ',' ','O',' ',' '],
            ['H','O','S','O','H'],
            [' ',' ','O',' ',' ']])
m.autoBonds()
m.addBond((3,1),(3,2),2)
m.addBond((3,3),(3,2),2)
add_molecule_layout(m)
