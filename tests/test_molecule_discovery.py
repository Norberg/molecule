import unittest
import os
import sqlite3
import datetime
from molecule.Persistence import Persistence

class TestMoleculeDiscovery(unittest.TestCase):
    def setUp(self):
        self.db_path = "test_progress.db"
        self.persistence = Persistence(self.db_path)
        self.player_name = "TestPlayer"
        self.player_id = self.persistence.create_player(self.player_name)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_get_seen_molecules(self):
        # Initially no molecules seen
        seen = self.persistence.get_seen_molecules(self.player_id)
        self.assertEqual(seen, set())

        # Mark some molecules as seen
        molecules = {"H2O", "CO2", "CH4"}
        self.persistence.update_player_stats(self.player_id, {}, molecules, {})

        # Verify seen molecules
        seen = self.persistence.get_seen_molecules(self.player_id)
        self.assertEqual(seen, molecules)

        # Non-existent player should return empty set
        self.assertEqual(self.persistence.get_seen_molecules(999), set())
        self.assertEqual(self.persistence.get_seen_molecules(None), set())

if __name__ == "__main__":
    unittest.main()
