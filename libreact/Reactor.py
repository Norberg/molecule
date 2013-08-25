import Reaction

class Reactor:
	def __init__(self, reactions):
		self.reactions = reactions

	def find_reactions(self, reactants):
		""" check if all elements needed for a reaction exists in
	 	    in the reacting elements. 
		    Return the reaction if it exist otherwise None
		"""
		reactants = Reaction.list_without_state(reactants)
		for reaction in self.reactions:
			if sublist_in_list(reaction.reactants, reactants):
				return reaction
		return None

	def react(self, reactants, temperature = 298):
		""" check if all elements needed for the reaction exists in
	 	    in the reacting elements and that the reaction is spontaneous
		    in the given temperature. 
		    Return the reaction if it will occur otherwise None
		"""
		reactionCml = self.find_reactions(reactants)		
		if reactionCml is None:
			return None
		reaction = Reaction.Reaction(reactionCml, reactants)
		if reaction.isSpontaneous(temperature):
			return reaction
		else:
			return None



def sublist_in_list(sublist, superlist):
	for e in sublist:
		if sublist.count(e) > superlist.count(e):
			return False
	return True
