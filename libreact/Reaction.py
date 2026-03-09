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
from __future__ import annotations

import re
from collections import Counter
from typing import Any, Iterator

from libcml import CachedCml


class Reaction:
    def __init__(self, cml: Any, reacting_elements: list[str]) -> None:
        self.cml = cml
        self.products = cml.products
        self.reactants: list[str] = list(cml.reactants)
        self.trace = False
        self.addStateToReactants(reacting_elements)
        verify(self.products)    
        verify(self.reactants)
        verifyReactionIsBalanced(self.products, self.reactants)    

    @property
    def products_stateless(self) -> list[str]:
        return list_without_state(self.products)
    
    @property
    def reactants_stateless(self) -> list[str]:
        return list_without_state(self.reactants)

    def __str__(self) -> str:
        return "Reaction(%s -> %s)" % (str(self.reactants), str(self.products))

    def addStateToReactants(self, reactants: list[str]) -> None:
        """ Take a list of reactans with state to populate the reaction with the same info"""
        for reactant in reactants:
            reactant_without_state = remove_state(reactant) 
            if reactant_without_state in self.reactants:
                self.reactants.remove(reactant_without_state)
                self.reactants.append(reactant)    

    def deltaEnthalpy(self) -> float:
        enthalpyReactants = self.sumEnthalpy(self.reactants, "reactants")
        enthalpyProducts = self.sumEnthalpy(self.products, "products")
        deltaEnthalpy = enthalpyProducts - enthalpyReactants
        if self.trace:
            print(f"deltaEnthalpy = enthalpyProducts - enthalpyReactants = {enthalpyProducts} - {enthalpyReactants}")
            print(f"deltaEnthalpy = {deltaEnthalpy} kJ/mol")
        return deltaEnthalpy

    def deltaEntropy(self) -> float:
        entropyReactants = self.sumEntropy(self.reactants, "reactants") / 1000.0  # J -> kJ
        entropyProducts = self.sumEntropy(self.products, "products") / 1000.0  # J -> kJ
        deltaEntropy = entropyProducts - entropyReactants
        if self.trace:
            print(f"deltaEntropy = entropyProducts - entropyReactants = {entropyProducts} - {entropyReactants}")
            print(f"deltaEntropy = {deltaEntropy} kJ/K·mol")
        return deltaEntropy

    def energyChange(self, T: float) -> float:
        deltaEnthalpy = self.deltaEnthalpy()
        deltaEntropy = self.deltaEntropy()
        free_energy = deltaEnthalpy - T * deltaEntropy
        if self.trace:
            print(f"Gibbs free energy (ΔG) = ΔH - T·ΔS = {deltaEnthalpy} kJ/mol - {T} K * {deltaEntropy} kJ/K·mol ")
            print(f"Gibbs free energy (ΔG) = {free_energy} kJ/mol")
        return free_energy

    def isSpontaneous(self, K: float = 298) -> bool:
        free_energy = self.energyChange(K)
        return free_energy < 0

    def sumEntropy(self, elements: list[str], text: str) -> float:
        total_entropy = 0
        for element in elements:
            formula, state = split_state(element)
            entropy = self.getMolecule(formula).get_state(state).entropy
            if entropy is None:
                raise Exception(f"Entropy is None for {element}")
            total_entropy += entropy
            if self.trace:
                print(f"Entropy {element}: {entropy} J/K", end=", ")
        if self.trace:
            print(f"Total entropy for {text}: {total_entropy} J/K")
        return total_entropy


    def sumEnthalpy(self, elements: list[str], text: str) -> float:
        total_enthalpy = 0
        for element in elements:
            formula, state = split_state(element)
            cml_state = self.getMolecule(formula).get_state(state)
            if cml_state is None:
                raise Exception(f"State {state} does not exist for {element}")
            enthalpy = cml_state.enthalpy
            if enthalpy is None:
                raise Exception(f"Enthalpy is None for {element}")
            total_enthalpy += enthalpy
            if self.trace:
                print(f"Enthalpy {element}: {enthalpy} J/K", end=", ")
        if self.trace:
            print(f"Total enthalpy for {text}: {total_enthalpy} J/K")
        return total_enthalpy
    
    def getMolecule(self, formula: str) -> Any:
        return CachedCml.getMolecule(formula)

    def getStates(self, elements: list[str]) -> Iterator[Any]:
        for element in elements:
            formula, state = split_state(element)
            molecule = self.getMolecule(formula)
            s = molecule.get_state(state)
            if s is None:
                raise Exception("Tried to read non existing state:(" 
                                 + state + ") for: "+ formula)
            else:
                yield s    
    
SPLIT_STATE_RE = re.compile(r"(\S+)\((.*)\)")

def split_state(molecule: str) -> tuple[str, str]:
    """return formula, state"""
    #regexp extract molecule and state from H20(aq)
    groups = SPLIT_STATE_RE.search(molecule)
    if groups is None:
        raise Exception("Not possible to extract state from:" + molecule)
    formula = groups.group(1)
    state = groups.group(2)
    return formula, state

def remove_state(molecule: str) -> str:
    if not molecule.endswith(")"):
        return molecule
    return split_state(molecule)[0]

def verify(elements: list[str]) -> None:
    """Sanity check of symbol name, make sure no zeros without preceeding digit have been used by mistake"""
    for element in elements:
        atom_numbers = [int(num) for num in re.findall(r"\d+", element)]
        if 0 in atom_numbers:
             raise Exception(f"Tried to create reaction with invalid values {element} in {elements}")

def list_without_state(molecules: list[str]) -> list[str]:
    """Return a list of molecules without any state """
    without_state: list[str] = []
    for molecule in molecules:
        without_state.append(remove_state(molecule))
    return without_state
    
def isSpontaneous(free_energy: float) -> bool:
    return free_energy < 0

def verifyReactionIsBalanced(products: list[str], reactants: list[str]) -> None:
    """Verify that the reaction is balanced"""
    productsAtoms = getAtomCount(products)
    reactantsAtoms = getAtomCount(reactants)
    if productsAtoms != reactantsAtoms:
        raise Exception(f"Reaction is not balanced for reactions {reactants} -> {products}   \n reactions atoms is {reactantsAtoms} != {productsAtoms} \ndiff being {diffCounters(productsAtoms,reactantsAtoms)}")

def getAtomCount(molecules: list[str]) -> Counter[str]:
    moleules = list_without_state(molecules)
    atom_count: Counter[str] = Counter()
    for molecule in moleules:
        atoms = re.findall(r"([A-Z][a-z]?)(\d*)", molecule)
        for atom, num in atoms:
            if num == '':
                num = 1
            else:
                num = int(num)
            atom_count[atom] += num
    return atom_count

def diffCounters(productsAtoms: Counter[str], reactantsAtoms: Counter[str]) -> Counter[str]:
    diff: Counter[str] = Counter()
    for atom in productsAtoms:
        if productsAtoms[atom] != reactantsAtoms[atom]:
            diff[atom] = productsAtoms[atom] - reactantsAtoms[atom]
    return diff
