import unittest

import pyglet

from game_state import GameState
from game_types import GameMode
from helper import Vector
from user_interface.menu import MapMenu


class Object(object):
    pass


class TestGameState(unittest.TestCase):
    def test_window_to_world_space(self):
        game_state = GameState()
        actual = game_state.window_to_world_space(Vector())
        self.assertEqual(Vector(-100, -100), actual, str(actual))

    def test_world_to_window_space(self):
        game_state = GameState()
        game_state.window_size = Vector(100, 100)

        position = Vector(1, 1)
        size = Vector(10, 10)
        self.assertEqual(None, game_state.world_to_window_space(position, size))

        position = Vector()
        size = Vector(10, 10)
        self.assertEqual(Vector(100, 100), game_state.world_to_window_space(position, size))

        game_state.world_offset = Vector(-100, 0)
        position = Vector()
        size = Vector(10, 10)
        self.assertEqual(None, game_state.world_to_window_space(position, size))

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
        game_state.window_size = Vector(1280, 720)
        game_state.update()
        self.assertEqual(world_offset_before, game_state.world_offset)

    def test_update_key_event_top_left(self):
        game_state = GameState()
        game_state.key_presses.up = True
        game_state.key_presses.left = True
        game_state.window_size = Vector(1280, 720)
        game_state.update()

        actual = game_state.world_offset
        self.assertEqual(Vector(105, 95), actual)

    def test_update_key_event_bottom_right(self):
        game_state = GameState()
        game_state.key_presses.down = True
        game_state.key_presses.right = True
        game_state.window_size = Vector(1280, 720)
        game_state.update()

        actual = game_state.world_offset
        self.assertEqual(Vector(95, 105), actual)

    def test_tick(self):
        def dummy():
            return -1, -2

        window = Object()
        window.get_size = dummy
        game_state = GameState()
        # noinspection PyTypeChecker
        game_state.tick(window)
        self.assertEqual(Vector(-1, -2), game_state.window_size)

    def test_tick_game(self):
        game_state = GameState()
        game_state.init('./tower_defense/res')
        game_state.tick_game()

    def test_tick_editor(self):
        game_state = GameState()
        game_state.init('./tower_defense/res')
        game_state.tick_editor()

    def test_tick_main_menu(self):
        game_state = GameState()
        game_state.init('./tower_defense/res')
        game_state.tick_main_menu()

    def test_tick_map_menu(self):
        game_state = GameState()
        game_state.init('./tower_defense/res')
        game_state.map_menu = MapMenu('./tower_defense/res/maps')
        game_state.tick_map_menu()
