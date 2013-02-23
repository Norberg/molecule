class Reaction:
	def __init__(self, consumed, result, areas = list()):
		self.verify(consumed)
		self.verify(result)
		self.consumed = consumed
		self.result = result
		self.areas = areas

	"""Sanity check of symbol name, make sure no zeros have been used by mistake"""
	def verify(self, elements):
		for element in elements:
			if "0" in element:
				raise Exception("Tried to create reaction with invalid values")
