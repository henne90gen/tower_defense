import shutil
from copy import deepcopy
from unittest import TestCase

import os

from tower_defense.game_state import GameState
from tower_defense.game_types import TileType, GameMode
from tower_defense.helper import Vector, MouseClick
from tower_defense.tiles.tile_map import Tile, TileMap, EditorTileMap, GameTileMap


class Object(object):
    pass


class TileMapTest(TestCase):
    def test_generate_tiles(self):
        tile_size = Vector(100, 100)

        def tile(x, y):
            return Tile(Vector(x, y), tile_size, TileType.BUILDING_GROUND)

        expected = {
            (0, 0): tile(0, 0),
            (1, 0): tile(1, 0),
            (0, 1): tile(0, 1),
            (1, 1): tile(1, 1)
        }
        max_tiles = Vector(2, 2)
        actual = TileMap.generate_tiles(max_tiles, tile_size)

        self.assertEqual(expected, actual)

    def test_new(self):
        tile_map = TileMap()
        game_state = GameState()
        test_path = "new.map"
        size = Vector(5, 5)
        tile_map.new(game_state, test_path, size)
        self.assertEqual(25, len(tile_map.tiles))
        self.assertEqual(test_path, tile_map.path)
        self.assertEqual(size, tile_map.max_tiles)
        os.remove(test_path)

    def test_save(self):
        game_state = GameState()
        test_map = "save.map"
        tile_map = TileMap()
        tile_map.path = test_map
        tile_map.max_tiles = Vector(5, 5)
        try:
            tile_map.save()
            self.assertTrue(os.path.exists(test_map))
            tile_map.load(game_state, test_map)  # make sure it can be loaded again
        finally:
            os.remove(test_map)

    def test_render(self):
        game_state = GameState()
        tile_map = TileMap()
        was_called = []

        def render(game_state, batch):
            was_called.append(0)

        tile = Object()
        tile.render = render
        tile.render_arrow = render
        tile_map.tiles = {(0, 0): tile}
        tile_map.render(game_state)
        self.assertEqual(1, len(was_called))

    @staticmethod
    def test_update_building():
        # no assertions, just making sure the code is run at all
        game_state = GameState()
        tile_map = TileMap()
        tile_map.update(game_state)

    @staticmethod
    def test_update_not_building():
        # no assertions, just making sure the code is run at all
        game_state = GameState()
        game_state.mode = GameMode.EDITOR
        tile_map = TileMap()
        tile_map.update(game_state)

    def test_mouse_click_handler_not_on_map(self):
        tile_map = TileMap()
        click = MouseClick()
        click.position = Vector(-1, -1)
        actual = tile_map.mouse_click_handler(None, click)
        expected = False
        self.assertEqual(expected, actual)

    def test_path_finding_no_start(self):
        tile_map = TileMap()
        tiles = deepcopy(tile_map.tiles)
        tile_map.path_finding()

        for tile in tiles:
            self.assertEqual(tiles[tile], tile_map.tiles[tile])

    def test_path_finding_no_finish(self):
        tile_map = TileMap()
        tile_map.tiles[(0, 0)].tile_type = TileType.START
        tiles = deepcopy(tile_map.tiles)
        tile_map.path_finding()

        for tile in tiles:
            self.assertEqual(tiles[tile], tile_map.tiles[tile])

    def test_path_finding_no_path(self):
        tile_map = TileMap()
        tile_map.tiles[(0, 0)].tile_type = TileType.START
        tile_map.tiles[(2, 2)].tile_type = TileType.FINISH

        tiles = deepcopy(tile_map.tiles)
        tile_map.path_finding()

        for tile in tiles:
            self.assertEqual(tiles[tile], tile_map.tiles[tile])

    def test_path_finding(self):
        tile_map = TileMap()
        tile_map.tiles[(0, 0)].tile_type = TileType.START
        tile_map.tiles[(1, 0)].tile_type = TileType.PATH
        tile_map.tiles[(2, 0)].tile_type = TileType.PATH
        tile_map.tiles[(2, 1)].tile_type = TileType.PATH
        tile_map.tiles[(2, 2)].tile_type = TileType.FINISH

        tiles = deepcopy(tile_map.tiles)
        tiles[(0, 0)].directions = [(1, 0)]
        tiles[(1, 0)].directions = [(1, 0)]
        tiles[(2, 0)].directions = [(0, 1)]
        tiles[(2, 1)].directions = [(0, 1)]
        tile_map.path_finding()

        for tile in tiles:
            self.assertEqual(tiles[tile], tile_map.tiles[tile])

    def test_has_start_node(self):
        tile_map = TileMap()
        self.assertFalse(tile_map.has_start_node)

        tile_map.tiles[(0, 0)].tile_type = TileType.START
        self.assertTrue(tile_map.has_start_node)

    def test_has_finish_node(self):
        tile_map = TileMap()
        self.assertFalse(tile_map.has_finish_node)

        tile_map.tiles[(0, 0)].tile_type = TileType.FINISH
        self.assertTrue(tile_map.has_finish_node)


class EditorTileMapTest(TestCase):
    def test_mouse_click_handler_on_map(self):
        tile_map = EditorTileMap()
        click = MouseClick()
        click.position = Vector(1, 1)
        click.button = 0
        actual = tile_map.mouse_click_handler(None, click)
        self.assertFalse(actual)

        tile_map = EditorTileMap()
        tile_map.tiles[(1, 1)].tile_type = TileType.START
        tile_map.tiles[(2, 2)].tile_type = TileType.FINISH
        click = MouseClick()
        click.position = Vector(1, 1)
        click.button = 1
        actual = tile_map.mouse_click_handler(None, click)
        self.assertTrue(actual)
        self.assertEqual(TileType.PATH, tile_map.tiles[(0, 0)].tile_type)

    def test_render(self):
        game_state = GameState()
        was_called = []

        def dummy(*args):
            was_called.append(0)

        tile_map = EditorTileMap()
        tile_map.tiles[(0, 0)].render_arrow = dummy
        tile_map.render(game_state)
        self.assertEqual(1, len(was_called))


class GameTileMapTest(TestCase):
    def test_render(self):
        game_state = GameState()
        was_called = []

        def dummy(*args):
            was_called.append(0)

        tile_map = GameTileMap()
        tile_map.tiles[(0, 0)].render_highlight = dummy
        tile_map.tiles[(0, 0)].highlighted = True
        tile_map.render(game_state)
        self.assertEqual(1, len(was_called))

    def test_mouse_click_handler(self):
        tile_map = GameTileMap()
        click = MouseClick()
        click.position = Vector(1, 1)
        click.button = 0
        actual = tile_map.mouse_click_handler(None, click)
        self.assertFalse(actual)

        tile_map = GameTileMap()
        click = MouseClick()
        click.position = Vector(1, 1)
        click.button = 1
        actual = tile_map.mouse_click_handler(None, click)
        self.assertTrue(actual)
        self.assertTrue(tile_map.tiles[(0, 0)].highlighted)

        actual = tile_map.mouse_click_handler(None, click)
        self.assertTrue(actual)
        self.assertFalse(tile_map.tiles[(0, 0)].highlighted)

        tile_map = GameTileMap()
        tile_map.tiles[(0,0)].tile_type = TileType.PATH
        click = MouseClick()
        click.position = Vector(1, 1)
        click.button = 1
        actual = tile_map.mouse_click_handler(None, click)
        self.assertTrue(actual)
        self.assertFalse(tile_map.tiles[(0, 0)].highlighted)
