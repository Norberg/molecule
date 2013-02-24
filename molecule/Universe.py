import glob, random
import pygame
import PyGameUtil,util,Bonds
from Reaction import Reaction
from Molecule import Molecule, MoleculeSprite
import Config

class Universe:
	"""Universe contains all fundamental particles and laws needed to get the universe to spin"""
	def __init__(self):
		print "Universe is initilazing" 
		self.moelcules = dict()
		self.__init__molecule_table()
		self.__init__reactions()
		Bonds.init__bonds()

	def __init__reactions(self):
		self.reactions = list()
		self.reactions.append(Reaction(["O","H+"], ["OH-"]))
		self.reactions.append(Reaction(["O","O"], ["O2"]))
		self.reactions.append(Reaction(["O","H2"], ["H2O"]))
		self.reactions.append(Reaction(["H+","H+"], ["H2"]))
		self.reactions.append(Reaction(["H+","OH-"], ["H2O"]))
		self.reactions.append(Reaction(["CH4","H2O"], ["CO"] + 3*["H2"]))
		self.reactions.append(Reaction(["CH4"] + 2*["O2"], ["CO2"] + 2*["H2O"]))
		self.reactions.append(Reaction(["CH4", "O2"], ["CO"] + 2*["H2O"]))
		self.reactions.append(Reaction(["NH3", "H2O"], ["NH4+"] + ["OH-"]))
		self.reactions.append(Reaction(2*["NH3"] + ["CO2"], ["CH4N2O"] + ["H2O"]))
		self.reactions.append(Reaction(["SO3", "H2O"], ["H2SO4"]))
		self.reactions.append(Reaction(["H2SO4"] + 2*["NaCl"], 2*["HCl"] + ["Na2SO4"]))

	def __init__molecule_table(self):
		print "init molecule table"
		self.molecule_layouts = dict()
		
		m = Molecule("O", 249, 161) #gas
		m.addAtoms([["O"]])
		self.add_molecule_layout(m)
		
		m = Molecule("H", 218, 114) #gas
		m.addAtoms([["O"]])
		self.add_molecule_layout(m)

		m = Molecule("OH-", -230, -11) #aq
		m.addAtoms([['O','H-']])
		self.add_molecule_layout(m)

		m = Molecule("H2", 0, 131) #gas
		m.addAtoms([['H','H']])
		self.add_molecule_layout(m)

		m = Molecule("H2O", -286, 70) #gas
		m.addAtoms([['H','O','H']])
		self.add_molecule_layout(m)
		
		m = Molecule("O2",0, 205) #gas
		m.addAtoms([['O','O']])
		m.addBond((1,1),(2,1),2)
		self.add_molecule_layout(m)
		
		m = Molecule("CO", -110, 197) #gas
		m.addAtoms([['C','O-']])
		m.addBond((1,1),(2,1),2)
		self.add_molecule_layout(m)
		
		m = Molecule("CO2", -394, 214) #gas
		m.addAtoms([['O','C','O']])
		m.addBond((1,1),(2,1),2)
		m.addBond((2,1),(3,1),2)
		self.add_molecule_layout(m)
		
		m = Molecule("CH4", -75, 186) #gas
		m.addAtoms([[' ','H',' '],
                            ['H','C','H'],
                            [' ','H',' ']])
		self.add_molecule_layout(m)
		
		m = Molecule("NH3", -46, 193) #gas
		m.addAtoms([['H',' ','H'],
                            [' ','N',' '],
                            [' ','H',' ']])
		m.autoBonds()
		m.addBond((1,1),(2,2))
		m.addBond((3,1),(2,2))
		self.add_molecule_layout(m)

		m = Molecule("NH4+", -132, 113) #aq
		m.addAtoms([[' ','H' ,' '],
                            ['H','N+','H'],
                            [' ','H' ,' ']])
		self.add_molecule_layout(m)
		
		m = Molecule("HCl", -92, 187) #gas
		m.addAtoms([['H','Cl']])
		self.add_molecule_layout(m)
		
		m = Molecule("NaCl", -411, 72) #solid
		m.addAtoms([['Na','Cl']])
		self.add_molecule_layout(m)
		
		m = Molecule("SO3", -396, 257) #gas
		m.addAtoms([['O',' ','O'],
                            [' ','S',' '],
                            [' ','O',' ']])
		m.addBond((1,1),(2,2),2)
		m.addBond((3,1),(2,2),2)
		m.addBond((2,3),(2,2),2)
		self.add_molecule_layout(m)

		m = Molecule("SO4+")
		m.addAtoms([[' ','O' ,' '],
                            ['O','S+','O'],
                            [' ','O' ,' ']])
		self.add_molecule_layout(m)
		
		m = Molecule("H2SO4", -814, 157) #liquid
		m.addAtoms([[' ',' ','O' ,' ',' '],
                            ['H','O','S+','O','H'],
                            [' ',' ','O' ,' ',' ']])
		m.autoBonds()
		m.addBond((3,1),(3,2),2)
		m.addBond((3,3),(3,2),2)
		self.add_molecule_layout(m)
		
		m = Molecule("Na2SO4")
		m.addAtoms([[' ', 'O', ' ','Na'],
                            ['O', 'S+','O',' '],
                            [' ', 'O', ' ',' '],
                            ['Na',' ', ' ',' ']])
		m.autoBonds()
		m.addBond((2,1),(2,2),2)
		m.addBond((1,2),(2,2),2)
		m.addBond((1,4),(2,3))
		m.addBond((4,1),(3,2))
		self.add_molecule_layout(m)
		
		m = Molecule("P4", 59, 280) #gas
		m.addAtoms([[' ','P',' ','P'],
                            ['P',' ','P',' ']])
		m.addBond((1,2),(2,1),3)
		m.addBond((2,1),(3,2),2)
		m.addBond((3,2),(4,1),3)
		self.add_molecule_layout(m)

		m = Molecule("CH4N2O", -319.2, 174) #aq
		m.addAtoms([[' ',' ','O',' ',' '],
                            [' ',' ','C',' ',' '],
                            ['H','N',' ','N','N'],
                            [' ','H',' ','H',' ']])
		m.autoBonds()
		m.addBond((3,1), (3,2),2)
		m.addBond((3,2),(2,3))
		m.addBond((3,2),(4,3))
		self.add_molecule_layout(m)
			

	def reaction_table(self, elem, effects):
		for reaction in self.reactions:
			if util.sublist_in_list(reaction.reactants, elem):
				#all elements needed for the reaction exists in the reacting elements
				temp = 298
				effect_names = list()
				for effect in effects:
					effect_names.append(effect.name)
					if effect.name == "Fire":
						temp = effect.temp
	
				print reaction.reactants, "+", effect_names, "->", reaction.products
				if reaction.isSpontaneous(temp):
					return reaction
				else:
					print "reaction was not spontanues at this temperature"
		
	def add_molecule_layout(self, molecule):
		if len(molecule.bond_layout) == 0:
			molecule.autoBonds()
		self.molecule_layouts[molecule.formula] = molecule
			
				
	def molecule_table(self, molecule):
		if self.molecule_layouts.has_key(molecule):
			return self.molecule_layouts[molecule]
		elif util.isAtom(molecule):
			return Molecule(molecule)
		else:
			raise Exception("No layout found for:" + molecule)
	
	def create_elements(self, elements, pos=None):
		list_of_elements = list()
		if pos != None:
			x, y = pos

		if isinstance(elements, basestring):
			elements = [elements] #elements is a string, wrap it in a list not to confuse for
		for element in elements:
			if pos != None and len(elements) > 1:
				pos = (x + random.randint(-50,50), y + random.randint(-50, 50))
			molecule = self.molecule_table(element)
			list_of_elements.append(MoleculeSprite(molecule, pos))
		return tuple(list_of_elements)

	def react(self, elements, areas):
		if len(elements) < 2:
			return
		if Config.current.DEBUG: print "Trying to see if some of this react:", elements
		reaction = self.reaction_table(elements, areas)
		if reaction != None:
			return reaction

universe = None
print "univers = None"
def createUniverse():
	global universe
	universe = Universe()
	universe.create_elements("H")
	print "Creaded the Universe"
