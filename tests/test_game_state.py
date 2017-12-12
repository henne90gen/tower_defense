import unittest

from game_state import GameState
from game_types import GameMode
from helper import Vector


class TestGameState(unittest.TestCase):
    def test_window_to_world_space(self):
        game_state = GameState()
        actual = game_state.window_to_world_space(Vector())
        self.assertEqual(Vector(-100, -100), actual, str(actual))

    def test_world_to_window_space(self):
        game_state = GameState()
        actual = game_state.world_to_window_space(Vector())
        self.assertEqual(Vector(100, 100), actual, str(actual))

    def test_world_to_index_space(self):
        game_state = GameState()

        actual = game_state.world_to_index_space(Vector())
        self.assertEqual((0, 0), actual, str(actual))

        actual = game_state.world_to_index_space(Vector(100, 100))
        self.assertEqual((1, 1), actual, str(actual))

        actual = game_state.world_to_index_space(Vector(50, 50))
        self.assertEqual((0, 0), actual, str(actual))

    def test_index_to_world_space(self):
        game_state = GameState()
        actual = game_state.index_to_world_space((0, 0))
        self.assertEqual(Vector(0, 0), actual, str(actual))

        actual = game_state.index_to_world_space((1, 0))
        self.assertEqual(Vector(100, 0), actual, str(actual))

        actual = game_state.index_to_world_space(Vector(1, 0))
        self.assertEqual(Vector(100, 0), actual, str(actual))

    def test_init(self):
        game_state = GameState()
        game_state.init("./tower_defense/res")

        self.assertIsNotNone(Vector(10, 10), game_state.tile_map.max_tiles)
        self.assertIsNotNone(100, len(game_state.tile_map.tiles))

    def test_clean_up(self):
        game_state = GameState()

        game_state.clean_up()

        self.assertEqual(0, len(game_state.mouse_clicks))
        self.assertEqual("", game_state.key_presses.text)
        self.assertEqual(False, game_state.key_presses.back_space)

    def test_update_no_key_event(self):
        game_state = GameState()
        world_offset_before = game_state.world_offset
        window_size = Vector(1280, 720)
        game_state.update(window_size)

        self.assertEqual(window_size, game_state.window_size)
        self.assertEqual(world_offset_before, game_state.world_offset)

    def test_update_key_event_top_left(self):
        game_state = GameState()
        game_state.key_presses.up = True
        game_state.key_presses.left = True
        window_size = Vector(1280, 720)
        game_state.update(window_size)

        actual = game_state.world_offset
        self.assertEqual(Vector(105, 95), actual)

    def test_update_key_event_bottom_right(self):
        game_state = GameState()
        game_state.key_presses.down = True
        game_state.key_presses.right = True
        window_size = Vector(1280, 720)
        game_state.update(window_size)

        actual = game_state.world_offset
        self.assertEqual(Vector(95, 105), actual)

    def test_properties(self):
        game_state = GameState()
        game_state.mode = GameMode.NORMAL
        self.assertEqual(True, game_state.editor_mode)
        self.assertEqual(False, game_state.test_mode)
        self.assertEqual(False, game_state.building_mode)
