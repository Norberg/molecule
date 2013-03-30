
class State:
	def __init__(self, name, short, enthalpy, entropy):
		self.name = name
		self.short = short 
		self.enthalpy = enthalpy
		self.entropy = entropy
	def react(self):
		"""Return a list on elements if state change result in new componds"""
		pass

class Aqueues(State):
	def __init__(self, enthalpy, entropy, ions = list()):
		State.__init__(self, "Aqueous", "aq", enthalpy, entropy) 
		self.ions = ions	
	def react(self):
		return self.ions

class Solid(State):
	def __init__(self, enthalpy, entropy):
		State.__init__(self, "Solid", "s", enthalpy, entropy) 
class Liquid(State):
	def __init__(self, enthalpy, entropy):
		State.__init__(self, "Liquid", "l", enthalpy, entropy) 
class Gas(State):
	def __init__(self, enthalpy, entropy):
		State.__init__(self, "Gas", "g", enthalpy, entropy) 
