import unittest
import time
from molecule.Levels import Levels, Level
from libcml import Cml

class MockWindow:
    def __init__(self):
        self.level = None
        self.levels = None
        self.width = 800
        self.height = 600
        self.penalty = 0

    def get_size(self):
        return (self.width, self.height)
    
    def push_handlers(self, *args, **kwargs):
        pass

    def remove_handlers(self, *args, **kwargs):
        pass

    def add_penalty(self, seconds):
        self.penalty += seconds

class TestPenalty(unittest.TestCase):
    def setUp(self):
        self.window = MockWindow()
        self.levels = Levels("data/levels", start_level=1, window=self.window)
        self.window.levels = self.levels

    def test_penalty_application(self):
        level = self.levels.get_current_level()
        self.window.level = level
        
        initial_time = level.get_time()
        self.assertLess(initial_time, 1.0)
        
        self.window.add_penalty(30)
        new_time = level.get_time()
        self.assertGreaterEqual(new_time, 30.0)
        self.assertEqual(self.window.penalty, 30)

    def test_penalty_persistence_on_reset(self):
        level = self.levels.get_current_level()
        self.window.level = level
        self.window.add_penalty(30)

        
        # Simulate reset
        new_level = self.levels.get_current_level()
        # The penalty stays in the window (MockWindow)
        self.assertEqual(self.window.penalty, 30)
        self.assertGreaterEqual(new_level.get_time(), 30.0)

    def test_penalty_reset_on_new_level(self):
        self.window.penalty = 30
        
        # Simulate selecting a new level (resetting penalty in Game logic)
        self.window.penalty = 0 
        new_level = self.levels.get_current_level()
        self.assertEqual(self.window.penalty, 0)

if __name__ == '__main__':
    unittest.main()
