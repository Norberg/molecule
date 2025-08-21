import os
import unittest
import xml.etree.ElementTree as ET

REACTIONS_DIR = "data/reactions"

def iter_reaction_files():
    for name in sorted(os.listdir(REACTIONS_DIR)):
        if name.endswith('.cml'):
            yield os.path.join(REACTIONS_DIR, name)

def canonical_reaction_key(reactants, products):
    """Return a hashable canonical key (multiset for reactants/products)."""
    r_key = tuple(sorted(reactants))
    p_key = tuple(sorted(products))
    return (r_key, p_key)

def extract_reactions(path):
    tree = ET.parse(path)
    root = tree.getroot()
    for r in root.findall('.//reaction'):
        reactants = [m.get('title') for m in r.findall('./reactantList/molecule')]
        products = [m.get('title') for m in r.findall('./productList/molecule')]
        if reactants and products:
            yield reactants, products, path

class TestDuplicateReactions(unittest.TestCase):
    def test_no_duplicate_reactions_across_files(self):
        seen = {}
        duplicates = []
        for path in iter_reaction_files():
            for reactants, products, origin in extract_reactions(path):
                key = canonical_reaction_key(reactants, products)
                if key in seen:
                    duplicates.append((seen[key], origin, reactants, products))
                else:
                    seen[key] = origin
        if duplicates:
            lines = [
                f"Duplicate reaction {r}->{p} in {a} and {b}" for a, b, r, p in duplicates
            ]
            self.fail("\n" + "\n".join(lines))

if __name__ == '__main__':
    unittest.main()
