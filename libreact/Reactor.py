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
from libreact import Reaction
from libreact.MultiMap import MultiMap, MultiMapEntry


class ReactionEntryMapper:
    def __init__(self, cml_reaction):
        self.keys = cml_reaction.reactants
        self.value = cml_reaction

class Energy:
    def __init(self, type):
        self.type = type

class Reactor:
    def __init__(self, cml_reactions):
        self.reactions = cml_reactions
        self.reaction_map = MultiMap(cml_reactions, ReactionEntryMapper)
 
    def find_all_reactions(self, reactants):
        reactants = Reaction.list_without_state(reactants)
        if len(reactants) == 1:
            # Add a None to the end of the list to make sure that the next loop
            # will find all reactions that only have one reactant
            reactants.append(None)

        for reactant in reactants[:-1]:
            try:
                rs = self.reaction_map[reactant]
            except KeyError:
                continue

            for r in rs:
                if sublist_in_list(r.reactants, reactants):
                    yield r


    def find_reactions(self, reactants):
        """ check if all elements needed for a reaction exists in
             in the reacting elements. 
            Return the reactions, or empty set if none exists
        """
        return set(self.find_all_reactions(reactants))

    def react(self, reactants, K = 298, trace = False, energy_source = []):
        """ check if all elements needed for the reaction exists in
             in the reacting elements and that the reaction is spontaneous
            in the given temperature. 
            Return the reaction if it will occur otherwise None
        """
        reactionCmls = self.find_reactions(reactants)

        if len(reactionCmls) == 0 and trace:
            print("No reaction found for this reactants")
        elif len(reactionCmls) == 0:
            return None

        reactions = list()

        for reactionCml in reactionCmls:
            additional_energy = 0
            if len(reactionCml.requirements) > 0 and not all([req.type in [e for e in energy_source] for req in reactionCml.requirements]):
                if trace:
                    print(f"Reaction {reactionCml.reactants} -> {reactionCml.products} requires {reactionCml.requirements} to occur where only {energy_source} is available.")
                continue
            elif len(reactionCml.requirements) > 0:
                additional_energy = sum([req.molar_energy for req in reactionCml.requirements])
                if trace:
                    print(f"additional_energy = {additional_energy} for reaction {reactionCml.reactants} -> {reactionCml.products} with requirements {reactionCml.requirements}")

            r = Reaction.Reaction(reactionCml, reactants)
            reactions.append((r.energyChange(K) - additional_energy, r))
        
        if len(reactions) == 0:
            return None

        free_energy, reaction = min(reactions)
 
        if len(reactions) > 1 and trace:
            print("Multiple possible reactions:")
            for t in reactions:
                r = t[1]
                energy = t[0]
                print("Reactants:", r.reactants,
                      "Products:", r.products,
                      "Energy:", energy)
        
        if Reaction.isSpontaneous(free_energy):
            if trace:
                print(f"\nfree_energy is {free_energy} for reaction at {K}K !")
                reaction.trace = True
                reaction.isSpontaneous(K)
            return reaction
        elif trace:
            print(f"\nfree_energy is not enough for reaction at {K}K !")
            reaction.trace = True
            reaction.isSpontaneous(K)
            return None
        else:
            return None



def sublist_in_list(sublist, superlist):
    for e in sublist:
        if sublist.count(e) > superlist.count(e):
            return False
    return True