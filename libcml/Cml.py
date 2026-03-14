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
from collections.abc import Iterable
from typing import TYPE_CHECKING, TypeAlias
import xml.etree.ElementTree as etree
import operator
from enum import Enum

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element as _Element
    from xml.etree.ElementTree import ElementTree as _ElementTree
    ETElement: TypeAlias = _Element[str]
    ETTree: TypeAlias = _ElementTree[ETElement]
else:
    ETElement = etree.Element
    ETTree = etree.ElementTree


class Atom:
    def __init__(
        self,
        id: str = "",
        element: str = "",
        charge: int = 0,
        x: float = 0.0,
        y: float = 0.0,
        z: float | None = None,
    ) -> None:
        self.id = id
        self.elementType = element
        self.formalCharge = charge
        self.x = x
        self.y = y
        self.z = z

    @property
    def pos(self) -> tuple[float, float]:
        return (self.x, self.y)

    @property
    def x_str(self) -> str:
        return str(self.x)
    @property
    def y_str(self) -> str:
        return str(self.y)
    @property
    def z_str(self) -> str:
        return str(self.z)

class Bond:
    def __init__(self, atomA: Atom | None = None, atomB: Atom | None = None, bonds: int = 0) -> None:
        """ Bond from atomA to atomB having nr of bonds"""
        self.atomA = atomA
        self.atomB = atomB
        self.bonds = bonds

    @property
    def atomRefs2(self) -> str:
        return f"{self.atomA.id if self.atomA else ''} {self.atomB.id if self.atomB else ''}"

class State:
    STATE_MAP = {"Aqueous":"aq", "Solid":"s", "Gas":"g", "Liquid":"l"}
    def __init__(
        self,
        name: str = "",
        enthalpy: float | None = None,
        entropy: float | None = None,
        ions: list[str] | None = None,
        emitter: str | None = None,
        emitter_color: str | None = None,
    ) -> None:
        self.name = name
        self.enthalpy = enthalpy
        self.entropy = entropy
        self.ions = ions
        # Optional visual emitter identifier (string referencing emitter registry name)
        self.emitter = emitter
        # Optional hex color (e.g. #FF00AA) used by certain emitters (e.g. fireworks)
        self.emitter_color = emitter_color


    def __str__(self) -> str:
        return "State: " + self.name

    @property
    def short(self) -> str:
        return self.STATE_MAP[self.name]

    @property
    def ions_str(self) -> str:
        if self.ions is None:
            return ""
        str = ""
        for ion in self.ions:
            str +=","+ion
        return str[1:]


class Reaction:
    def __init__(
        self,
        reactants: list[str] | None = None,
        products: list[str] | None = None,
        title: str | None = None,
        description: str | None = None,
        tags: list[str] | None = None,
        requirements: list["Requirement"] | None = None,
    ) -> None:
        self.reactants = reactants
        self.products = products
        self.title = title
        if description is None:
            self.description = title
        else:
            self.description = description
        self.tags = tags or []
        self.requirements = requirements or []

    @property
    def reaction_key(self) -> str:
        from libreact.Reaction import list_without_state
        reactants = list_without_state(self.reactants)
        products = list_without_state(self.products)
        return "_".join(reactants) + "_to_" + "_".join(products)

class Effect:
    def __init__(
        self,
        title: str | None = None,
        value: float | None = None,
        x2: float | None = None,
        y2: float | None = None,
        molecules: list[str] | None = None,
    ) -> None:
        self.title = title
        self.value = value
        self.molecules = molecules or []
        self.x2 = x2
        self.y2 = y2


class Requirement:
    class EnergyType(Enum):
        UV_LIGHT = "UV light"
        ELECTROLYSIS = "Electrolysis"
        PH_MIN = "pH min"
        PH_MAX = "pH max"

    def __init__(self, type: str, value: float) -> None:
        self.type = Requirement.EnergyType(type)
        self.value = value

    def __str__(self) -> str:
        return f"Requirement: {self.type} {self.value}"
    
    def __repr__(self) -> str:
        return self.__str__()
    
class Cml:
    NS = "{http://www.xml-cml.org/schema}"

    def treefind(self, xpath: str) -> ETElement | None:
        return self.xmlfind(self.tree, xpath)

    def xmlfind(self, document: ETTree, xpath: str) -> ETElement | None:
        element = document.find(xpath)
        if element is None:
            element = self.tree.find(self.NS + xpath)
        return element
    
    def parseReaction(self, reactionTag: ETElement) -> Reaction:
        reaction = Reaction()
        reaction.title = reactionTag.get("title")
        for part in reactionTag:
            if part.tag.endswith("productList"):
                reaction.products = self.parseMoleculeList(part)
            elif part.tag.endswith("reactantList"):
                reaction.reactants = self.parseMoleculeList(part)
            elif part.tag.endswith("requirementList"):
                reaction.requirements = self.parseRequirements(part)
            elif part.tag.endswith("description"):
                reaction.description = part.text
            elif part.tag.endswith("tagList"):
                reaction.tags = [tag.text for tag in part if tag.text is not None]
        return reaction

    def parseMoleculeList(self, moleculesTag: ETElement) -> list[str]:
        molecules: list[str] = []
        for molecule in moleculesTag:
            molecules.append(molecule.attrib["title"])
        return molecules
    
    def parseRequirements(self, requirementsTag: ETElement) -> list[Requirement]:
        requirements: list[Requirement] = []
        for requirement in requirementsTag:
            type = requirement.attrib["type"]
            if "value" in requirement.attrib:
                value = float(requirement.attrib["value"])
            elif "molar_energy" in requirement.attrib:
                value = float(requirement.attrib["molar_energy"])
            else:
                raise Exception(f"Requirement missing value in {requirement.attrib}")
            requirements.append(Requirement(type, value))
        return requirements

    def writeReaction(self, reaction: Reaction | None, parrentTag: ETElement) -> None:
        if reaction is None:
            return
        tagReaction = etree.SubElement(parrentTag, "reaction")
        if reaction.title != None:
            tagReaction.set("title", reaction.title)
        if reaction.products != None:
            tagProducts = etree.SubElement(tagReaction, "productList")
            self.writeReactionMolecules(reaction.products, tagProducts)
        if reaction.reactants != None:
            tagReactants = etree.SubElement(tagReaction, "reactantList")
            self.writeReactionMolecules(reaction.reactants, tagReactants)

    def writeReactionMolecules(self, products: list[str], parrentTag: ETElement) -> None:
        for product in products:
            etree.SubElement(parrentTag, "molecule", {"title":product})

    def parseText(self, tagname: str) -> str:
        tag = self.treefind(tagname)
        return tag.attrib["text"]


class Level(Cml):
    LEVEL_TAG = "level"
    MOLECULE_LIST = "moleculeList"
    EFFECT_LIST = "effectList"
    VICTORY_CONDITION = "victoryCondition"
    OBJECTIVE = "objective"
    HINT = "hint"
    INVENTORY_LIST = "inventoryList"

    def __init__(self) -> None:
        self.tree: ETTree | None = None
        self.molecules: list[str] = []
        self.effects: list[Effect] = []
        self.objective: str | None = None
        self.victory_condition: list[str] = []
        self.hint: str | None = None
        self.zoom = 1.0
        self.inventory: list[str] = []
        self.aqueous_not_draggable = False

    def parse(self, filename: str) -> None:
        self.tree = etree.parse(filename)
        self.zoom = float(self.tree.getroot().attrib.get("zoom", self.zoom))
        drag_attr = self.tree.getroot().attrib.get("aqueousNotDraggable")
        if drag_attr is not None:
            self.aqueous_not_draggable = drag_attr.lower() == "true"

        molecule_list_tag = self.treefind(self.MOLECULE_LIST)
        self.molecules = self.parseMoleculeList(molecule_list_tag)

        victory_tag = self.treefind(self.VICTORY_CONDITION)
        self.victory_condition = self.parseMoleculeList(victory_tag)

        effect_tag = self.treefind(self.EFFECT_LIST)
        self.parseEffectList(effect_tag)

        self.objective = self.parseText(self.OBJECTIVE)
        self.hint = self.parseText(self.HINT)
        self.reactions_hint = self.parseReactionHints(self.treefind(self.HINT+ "/reactions"))
        inventory_list_tag = self.treefind(self.INVENTORY_LIST)
        if inventory_list_tag is not None:
            self.inventory = self.parseMoleculeList(inventory_list_tag)

    def parseReactionHints(self, hint_tag: ETElement | None) -> list[Reaction]:
        if hint_tag is None:
            return []
        hints: list[Reaction] = []
        for hint in hint_tag:
            r = self.parseReaction(hint)
            hints.append(r)
        return hints

    def parseEffectList(self, effect_list_tag: ETElement) -> None:
        for effect_tag in effect_list_tag:
            effect = self.parseEffect(effect_tag)
            self.effects.append(effect)

    def parseEffect(self, effect_tag: ETElement) -> Effect:
        effect = Effect()
        effect.title = effect_tag.attrib["title"]
        if "value" in effect_tag.attrib:
            effect.value = float(effect_tag.attrib["value"])
        effect.x2 = float(effect_tag.attrib["x2"])
        effect.y2 = float(effect_tag.attrib["y2"])
        effect.molecules = self.parseMoleculeList(effect_tag)

        return effect

    def write(self, filename: str) -> None:
        raise NotImplementedError

class Reactions(Cml):
    def __init__(self) -> None:
        self.tree: ETTree | None = None
        self.reactions: list[Reaction] = []

    def parse(self, filename: str) -> None:
        import os
        self.reactions = []  # reset
        if os.path.isdir(filename):
            # load every .cml file in directory (non-recursive) and merge
            files = sorted([f for f in os.listdir(filename) if f.endswith('.cml')])
            for f in files:
                path = os.path.join(filename, f)
                try:
                    tree = etree.parse(path)
                except Exception as e:
                    # skip unreadable file
                    continue
                self.parseReactions(tree.getroot())
        else:
            self.tree = etree.parse(filename)
            self.parseReactions(self.tree.getroot())


    def parseReactions(self, reactions: ETElement) -> None:
        for reaction in reactions:
            r = self.parseReaction(reaction)
            self.reactions.append(r)

    def empty_cml(self) -> ETTree:
        reactions = etree.Element("reactions")
        return etree.ElementTree(reactions)

    def write(self, filename: str) -> None:
        if self.tree is None:
            self.tree = self.empty_cml()

        self.writeReactions()
        self.tree.write(filename)

    def writeReactions(self) -> None:
        reactionsTag = self.tree.getroot()
        for reaction in self.reactions:
            self.writeReaction(reaction, reactionsTag)



class Molecule(Cml):
    ATOM_ARRAY = 'atomArray'
    BOND_ARRAY = 'bondArray'
    PROPERTY_LIST = "propertyList"
    STATES = PROPERTY_LIST+"/[@title='states']"
    PROPERTY = PROPERTY_LIST+"/[@title='property']"
    MOLECULE = "molecule"
    STATE_MAP = {"aq": "Aqueous", "s" : "Solid", "g" : "Gas", "l" : "Liquid"}
    def __init__(self) -> None:
        self.atoms: dict[str, Atom] = {}
        self.bonds: list[Bond] = []
        self.states: dict[str, State] = {}
        self.tree: ETTree | None = None
        self.property: dict[str, float | str] = {}

    def __str__(self) -> str:
        return "Molecule: " + str(self.atoms)

    def getDigits(self, string: str) -> int:
        temp = [s for s in string if s.isdigit()]
        string = ""
        for t in temp:
            string += t
        return int(string)

    @property
    def atoms_sorted(self) -> list[Atom]:
        return sorted(self.atoms.values(), key=lambda x:self.getDigits(x.id))

    @property
    def is_atom(self) -> bool:
        if len(self.atoms) == 1:
            return True
        else:
            return False

    def get_state(self, shortform: str) -> State | None:
        statename = self.STATE_MAP[shortform]
        if statename in self.states:
            return self.states[statename]
        else:
            return None

    def printer(self) -> None:
        print("Atoms:")
        for atom in self.atoms.values():
            print(atom.id, atom.elementType)
        print("Bonds:")
        for bond in self.bonds:
            print(bond.atomA.id, "->", bond.atomB.id, bond.bonds, "bonds")

    def min_pos(self) -> tuple[float, float, float]:
        min_x = min(self.atoms.values(), key=lambda a:a.x).x
        min_y = min(self.atoms.values(), key=lambda a:a.y).y
        z_values = [a.z for a in self.atoms.values() if a.z is not None]
        min_z = min(z_values) if z_values else 0.0
        return (min_x, min_y, min_z)

    def max_pos(self) -> tuple[float, float, float]:
        max_x = max(self.atoms.values(), key=lambda a:a.x).x
        max_y = max(self.atoms.values(), key=lambda a:a.y).y
        z_values = [a.z for a in self.atoms.values() if a.z is not None]
        max_z = max(z_values) if z_values else 0.0
        return (max_x, max_y, max_z)

    def normalize_pos(self) -> None:
        """ normalize position to be as close to (0,0,[0]) as possible """
        adj_x, adj_y, adj_z = self.min_pos()

        for atom in self.atoms.values():
            atom.x -= adj_x
            atom.y -= adj_y
            if atom.z is not None:
                atom.z -= adj_z

    def parse(self, filename: str) -> None:
        etree.register_namespace("", self.NS)
        self.tree = etree.parse(filename)
        self.parseAtoms(self.treefind(self.ATOM_ARRAY))
        self.parseBonds(self.treefind(self.BOND_ARRAY))
        self.parseStates(self.treefind(self.STATES))
        self.parseProperties(self.treefind(self.PROPERTY))

    def parseAtoms(self, atoms: ETElement) -> None:
        for atom in atoms:
            new = Atom()
            new.id = atom.attrib["id"]
            new.elementType = atom.attrib["elementType"]
            try:
                new.x = float(atom.attrib["x2"])
                new.y = float(atom.attrib["y2"])
            except KeyError:
                new.x = float(atom.attrib["x3"])
                new.y = float(atom.attrib["y3"])
                new.z = float(atom.attrib["z3"])
            try:
                new.formalCharge = int(atom.attrib["formalCharge"])
            except KeyError:
                new.formalCharge = 0
                pass
            self.atoms[new.id] = new

    def parseBonds(self, bonds: ETElement | None) -> None:
        if bonds == None:
            return
        for bond in bonds:
            new = Bond()
            atomRefs = bond.attrib["atomRefs2"].split()
            new.atomA = self.atoms[atomRefs[0]]
            new.atomB = self.atoms[atomRefs[1]]
            new.bonds = int(bond.attrib["order"])
            self.bonds.append(new)

    def parseStates(self, states: ETElement | None) -> None:
        if states == None:
            return
        for state in states:
            name = state.attrib["title"]
            emitter = state.attrib.get("emitter")
            emitter_color = state.attrib.get("emitterColor") or state.attrib.get("emitter_color")
            new_state = State(name, emitter=emitter, emitter_color=emitter_color)
            self.states[name] = new_state
            for property in state:
                title = property.attrib["title"]
                if title == "entropy":
                    new_state.entropy = float(property[0].text)
                elif title == "enthalpy":
                    new_state.enthalpy = float(property[0].text)
                elif title == "ions":
                    new_state.ions = self.parseIons(property)

    def parseProperties(self, properties: ETElement | None) -> None:
        if properties == None:
            return
        for property in properties:
            name = property.attrib["title"]
            if property.text is None:
                continue
            try:
                self.property[name] = float(property.text)
            except ValueError:
                self.property[name] = property.text

    def parseIons(self, ions: list[ETElement]) -> list[str]:
        reaction = self.parseReaction(ions[0])
        return reaction.products or []


    def empty_cml(self) -> ETTree:
        molecule = etree.Element("molecule")
        atomArray = etree.SubElement(molecule, "atomArray")
        bondArray = etree.SubElement(molecule, "bondArray")
        return etree.ElementTree(molecule)

    def write(self, filename: str) -> None:
        if self.tree is None:
            self.tree = self.empty_cml()

        self.writeAtoms()
        self.writeBonds()
        self.writeStates()
        self.writeProperties()
        self.tree.write(filename)

    def writeBonds(self) -> None:
        bondArray = self.treefind(self.BOND_ARRAY)
        if bondArray == None:
            return
        bondArray.clear() # Remove all old entires
        for bond in self.bonds:
            attrib = {"atomRefs2" : bond.atomRefs2,
                      "order" : str(bond.bonds)}
            etree.SubElement(bondArray,"bond", attrib)

    def writeAtoms(self) -> None:
        atomArray = self.treefind(self.ATOM_ARRAY)
        atomArray.clear() # Remove all old entires
        for atom in self.atoms.values():
            if atom.z is None:
                attrib = {"x2":atom.x_str,
                          "y2": atom.y_str}
            else:
                attrib = {"x3":atom.x_str,
                          "y3": atom.y_str,
                          "z3": atom.z_str}
            if atom.formalCharge != 0:
                attrib["formalCharge"] = str(atom.formalCharge)

            attrib["id"] = atom.id
            attrib["elementType"] = atom.elementType
            etree.SubElement(atomArray,"atom", attrib)

    def writeStates(self) -> None:
        states = self.treefind(self.STATES)
        if states is None:
            molecule = self.tree.getroot()
            states = etree.SubElement(molecule, "propertyList",
                                      {"title":"states"})
        else:
            states.clear() # Remove all old entires
            states.attrib["title"] = "states"

        for state in self.states.values():
            attrib = {"title": state.name}
            if state.emitter:
                attrib["emitter"] = state.emitter
            if state.emitter_color:
                attrib["emitterColor"] = state.emitter_color
            stateTag = etree.SubElement(states, "propertyList", attrib)
            self.writeEnthalpy(state, stateTag)
            self.writeEntropy(state, stateTag)
            self.writeIons(state.ions, stateTag)

    def writeEnthalpy(self, state: State, stateTag: ETElement) -> None:
        if state.enthalpy is None:
            return
        tagEnthalpy = etree.SubElement(stateTag, "property",
                                       {"title": "enthalpy"})
        scalar = etree.SubElement(tagEnthalpy, "scalar",
                                  {"units":"units:molar_energy"})
        scalar.text = str(state.enthalpy)

    def writeEntropy(self, state: State, stateTag: ETElement) -> None:
        if state.entropy is None:
            return
        tagEntropy = etree.SubElement(stateTag, "property",
                                       {"title": "entropy"})
        scalar = etree.SubElement(tagEntropy, "scalar",
                                  {"units":"units:molar_energy"})
        scalar.text = str(state.entropy)

    def writeIons(self, ions: list[str] | None, parrentTag: ETElement) -> None:
        if ions is None or len(ions) == 0:
            return
        r = Reaction(None, ions)
        tagIons = etree.SubElement(parrentTag, "property",
                                       {"title": "ions"})

        self.writeReaction(r, tagIons)

    def writeProperties(self) -> None:
        properties = self.treefind(self.PROPERTY)
        if properties is None:
            molecule = self.tree.getroot()
            properties = etree.SubElement(molecule, "propertyList",
                                      {"title":"property"})
        else:
            properties.clear() # Remove all old entires
            properties.attrib["title"] = "property"

        for name, value in self.property.items():
            propertyTag = etree.SubElement(properties, "property",
                                           {"title":name})
            propertyTag.text = str(value)

class Campaign(Cml):
    def __init__(self) -> None:
        self.pages: list[list[tuple[str, str, list[str]]]] = []

    def parse(self, filename: str) -> None:
        import os
        self.tree = etree.parse(filename)
        root = self.tree.getroot()
        base_dir = os.path.dirname(filename)
        
        self.pages = []
        for page_elem in root.findall('page'):
            biomes = []
            for biome_elem in page_elem.findall('biome'):
                name = biome_elem.get('name')
                icon = biome_elem.get('icon')
                level_paths = []
                for level_elem in biome_elem.findall('level'):
                    fname = level_elem.get('file')
                    # Look in levels/ subdirectory first if file exists there
                    levels_path = os.path.join(base_dir, "levels", fname)
                    if os.path.exists(levels_path):
                        level_paths.append(levels_path)
                    else:
                        level_paths.append(os.path.join(base_dir, fname))
                biomes.append((name, icon, level_paths))
            self.pages.append(biomes)

    def write(self, filename: str) -> None:
        raise NotImplementedError
