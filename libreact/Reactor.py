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

class Reactor:
    def __init__(self, cml_reactions):
        self.reactions = cml_reactions
        self.reaction_map = MultiMap(cml_reactions, ReactionEntryMapper)
 
    def find_all_reactions(self, reactants):
        reactants = Reaction.list_without_state(reactants)
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

    def react(self, reactants, K = 298, trace = False):
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
            r = Reaction.Reaction(reactionCml, reactants)
            reactions.append((r.energyChange(K), r))
        
        reaction = min(reactions)[1]
 
        if len(reactions) > 1 and trace:
            print("Multiple possible reactions:")
            for t in reactions:
                r = t[1]
                energy = t[0]
                print("Reactants:", r.reactants,
                      "Products:", r.products,
                      "Energy:", energy)
        
        if reaction.isSpontaneous(K):
            return reaction
        elif trace:
            print("free_energy wasnt enough for reaction!")
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

