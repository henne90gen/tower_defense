import unittest

from game_state import GameState
from helper import Vector


class TestGameState(unittest.TestCase):
    def test_window_to_world_space(self):
        game_state = GameState()
        actual = game_state.window_to_world_space(Vector())
        self.assertEqual(Vector(-100, -100), actual, str(actual))
