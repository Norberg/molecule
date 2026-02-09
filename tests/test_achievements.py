
import unittest
import sqlite3
import os
import tempfile
import shutil
from molecule.Achievements import AchievementManager
from molecule.Persistence import Persistence
from unittest.mock import MagicMock

class TestAchievements(unittest.TestCase):
    def setUp(self):
        # Use a temporary database for testing
        self.test_dir = tempfile.mkdtemp()
        db_path = os.path.join(self.test_dir, "test_progress.db")
        self.persistence = Persistence(db_path)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_achievement_manager_init(self):
        manager = AchievementManager()
        self.assertEqual(len(manager.achievements), 5)
        self.assertEqual(manager.achievements[0].key, "molecule_discover")

    def test_check_unlocks(self):
        manager = AchievementManager()
        ach = manager.achievements[0] # molecule_discover: 15, 30, 50
        
        # Test checking with 0
        self.assertEqual(ach.check(0, set()), [])
        
        # Test checking with 15 (Bronze)
        self.assertEqual(ach.check(15, set()), ["bronze"])
        
        # Test checking with 30 (Silver), when Bronze already unlocked
        self.assertEqual(ach.check(30, {"bronze"}), ["silver"])
        
        # Test checking with 50 (Gold), when Bronze and Silver already unlocked
        self.assertEqual(ach.check(50, {"bronze", "silver"}), ["gold"])
        
        # Test multiple unlocks at once (e.g. big jump in stats)
        self.assertEqual(set(ach.check(50, set())), {"bronze", "silver", "gold"})

    def test_persistence_integration(self):
        player_id = self.persistence.create_player("TestPlayer")
        
        # Manually unlock an achievement
        self.persistence.unlock_achievement(player_id, "test_key", "bronze")
        
        # Retrieve it
        achievements = self.persistence.get_player_achievements(player_id)
        self.assertEqual(len(achievements), 1)
        self.assertEqual(achievements[0]["key"], "test_key")
        self.assertEqual(achievements[0]["level"], "bronze")
        self.assertIn("unlocked_at", achievements[0])
        self.assertIsNotNone(achievements[0]["unlocked_at"])

    def test_full_check_flow(self):
        player_id = self.persistence.create_player("TestPlayer")
        manager = AchievementManager()
        
        # Mock persistence data methods to simulate game progress
        mock_persistence = MagicMock(wraps=self.persistence)
        mock_persistence.get_seen_molecules.return_value = {"H2O", "O2", "H2", "CO2", "CH4", "C6H12O6", "NaCl", "HCl", "NaOH", "NH3", "NO2", "SO2", "O3", "He", "Ne"} # 15 molecules
        mock_persistence.get_performed_reactions.return_value = [{"total_count": 10} for _ in range(15)] # 15 unique, 150 total
        mock_persistence.get_created_molecules.return_value = {"H2O": 200} # 200 created
        mock_persistence.get_completed_levels.return_value = {"level1", "level2", "level3", "level4", "level5", "level6", "level7", "level8", "level9", "level10"} # 10 levels
        
        # Test stats gathering
        stats = manager.get_player_stats(player_id, mock_persistence)
        self.assertEqual(stats["molecule_discover"], 15)
        self.assertEqual(stats["reaction_discover"], 15)
        self.assertEqual(stats["reactionist"], 150)
        self.assertEqual(stats["molecule_maker"], 200)
        self.assertEqual(stats["level_crusher"], 10)

        # Run check
        new_unlocks = manager.check_and_unlock(player_id, mock_persistence)
        
        # Verify unlocks
        self.assertEqual(len(new_unlocks), 5)
        keys = {u["key"] for u in new_unlocks}
        self.assertEqual(keys, {"molecule_discover", "reaction_discover", "reactionist", "molecule_maker", "level_crusher"})
        

        
        # Let's verify just the mock calls first
        self.assertEqual(mock_persistence.unlock_achievement.call_count, 5)

if __name__ == '__main__':
    unittest.main()

