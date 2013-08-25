import Cml
__cml_cache = dict()

def getMolecule(element):
	filename = "data/molecule/%s.cml" % element
	return getMoleculeCml(filename)

def getMoleculeCml(filename):
	global __cml_cache
	if __cml_cache.has_key(filename):
		return __cml_cache[filename]
	
	m = Cml.Molecule()
	m.parse(filename)
	__cml_cache[filename] = m
	return m
				
