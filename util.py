
def sublist_in_list(sublist, superlist):
	for e in sublist:
		if sublist.count(e) > superlist.count(e):
			return False
	return True

def isAtom(symbol):
	symbol = symbol.split("-")[0].split("+")[0] #Remove +/-
	if len(symbol) == 1 and symbol.isalpha(): # H, O, F etc.
		return True
	elif len(symbol) == 2 and symbol.isalpha() and symbol[1].islower(): #Fe, Mg, Na etc.
		return True
	elif len(symbol) == 3 and symbol.isalpha() and symbol[1:3].islower(): #Uut, Uup, Uus etc.
		return True
	else:
		return False
