import glob, os, unittest
from libcml import Cml
from libreact.Reaction import remove_state

class TestReactionHintOrder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Load all dataset reactions once
        rx = Cml.Reactions()
        rx.parse("data/reactions")
        cls.dataset = rx.reactions
        # Build mapping from tuple of reactant multiset signature to list of reactions (preserve order lists)
        cls.index = {}
        for r in cls.dataset:
            sig = tuple(sorted(remove_state(x) for x in r.reactants))
            cls.index.setdefault(sig, []).append(r)

    def test_hint_reactant_order_matches_dataset(self):
        level_files = sorted(glob.glob(os.path.join("data/levels", "*.cml")))
        problems = []
        for path in level_files:
            lvl = Cml.Level()
            lvl.parse(path)
            hints = getattr(lvl, "reactions_hint", [])
            if not hints:
                continue
            for hint_rx in hints:
                sig = tuple(sorted(remove_state(x) for x in hint_rx.reactants))
                candidates = self.index.get(sig, [])
                if not candidates:
                    # No dataset reaction with same multiset; skip (could be level-specific)
                    continue
                # If any candidate has identical ordered reactants list_without_state match, accept
                ordered = [remove_state(x) for x in hint_rx.reactants]
                dataset_match = any([remove_state(x) for x in c.reactants] == ordered for c in candidates)
                if not dataset_match:
                    problems.append((path, ordered, [[remove_state(x) for x in c.reactants] for c in candidates]))
        if problems:
            lines = [f"{p[0]}: hint order {p[1]} not in dataset orders {p[2]}" for p in problems]
            self.fail("\n".join(lines))

if __name__ == '__main__':
    unittest.main()
