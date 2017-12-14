import unittest

import pyglet

from game_state import GameState
from game_types import TileType
from helper import Vector
from tiles.tile import Tile


class TileTest(unittest.TestCase):
    def test_eq(self):
        position = Vector()
        size = Vector()
        tile_type = TileType.BUILDING_GROUND
        tile = Tile(position, size, tile_type)
        self.assertEqual(tile, tile)
        self.assertNotEqual("", tile)

    def test_str(self):
        position = Vector()
        size = Vector()
        tile_type = TileType.BUILDING_GROUND
        tile = Tile(position, size, tile_type)
        self.assertEqual("Tile: (0, 0):(0, 0) - TileType.BUILDING_GROUND", str(tile))

    def test_next_type(self):
        position = Vector()
        size = Vector()
        tile_type = TileType.BUILDING_GROUND
        tile = Tile(position, size, tile_type)

        tile.next_type(True, True)
        expected = TileType.PATH
        self.assertEqual(expected, tile.tile_type)

        tile.next_type(True, True)
        expected = TileType.START
        self.assertEqual(expected, tile.tile_type)

        tile.next_type(True, True)
        expected = TileType.FINISH
        self.assertEqual(expected, tile.tile_type)

        tile.next_type(True, True)
        expected = TileType.BUILDING_GROUND
        self.assertEqual(expected, tile.tile_type)

    def test_next_type_not_allowed(self):
        position = Vector()
        size = Vector()
        tile_type = TileType.BUILDING_GROUND
        tile = Tile(position, size, tile_type)

        tile.next_type(False, False)
        expected = TileType.PATH
        self.assertEqual(expected, tile.tile_type)

        tile.next_type(False, False)
        expected = TileType.BUILDING_GROUND
        self.assertEqual(expected, tile.tile_type)

        tile.tile_type = TileType.PATH
        tile.next_type(True, False)
        expected = TileType.START
        self.assertEqual(expected, tile.tile_type)

        tile.tile_type = TileType.PATH
        tile.next_type(False, True)
        expected = TileType.FINISH
        self.assertEqual(expected, tile.tile_type)

    def test_get_screen_coordinates(self):
        game_state = GameState()
        game_state.window_size = Vector(100, 100)

        position = Vector(1, 1)
        size = Vector(10, 10)
        tile_type = TileType.BUILDING_GROUND
        tile = Tile(position, size, tile_type)
        self.assertEqual(None, tile.get_screen_coordinates(game_state))

        position = Vector()
        size = Vector(10, 10)
        tile_type = TileType.BUILDING_GROUND
        tile = Tile(position, size, tile_type)
        self.assertEqual((100, 100), tile.get_screen_coordinates(game_state))

        game_state.world_offset = Vector(-100, 0)
        position = Vector()
        size = Vector(10, 10)
        tile_type = TileType.BUILDING_GROUND
        tile = Tile(position, size, tile_type)
        self.assertEqual(None, tile.get_screen_coordinates(game_state))

    def test_render_label(self):
        game_state = GameState()
        game_state.window_size = Vector(100, 100)

        position = Vector()
        size = Vector(10, 10)
        tile_type = TileType.BUILDING_GROUND
        tile = Tile(position, size, tile_type)

        batch = pyglet.graphics.Batch()
        tile.render_label(game_state, batch)
        self.assertEqual(1, len(batch.top_groups))
        self.assertEqual(pyglet.text.layout.TextLayoutGroup, type(batch.top_groups[0]))

    def test_render_no_label(self):
        game_state = GameState()
        game_state.window_size = Vector(100, 100)

        position = Vector(1, 1)
        size = Vector(10, 10)
        tile_type = TileType.BUILDING_GROUND
        tile = Tile(position, size, tile_type)

        batch = pyglet.graphics.Batch()
        tile.render_label(game_state, batch)
        self.assertEqual(0, len(batch.top_groups))

    def test_render(self):
        game_state = GameState()
        game_state.init("./tower_defense/res")
        game_state.window_size = Vector(100, 100)

        position = Vector()
        size = Vector(10, 10)
        tile_type = TileType.BUILDING_GROUND
        tile = Tile(position, size, tile_type)

        batch = pyglet.graphics.Batch()
        tile.render(game_state, batch)
        self.assertEqual(1, len(batch.top_groups))
        self.assertEqual(pyglet.graphics.TextureGroup, type(batch.top_groups[0]))

        batch = pyglet.graphics.Batch()
        tile.tile_type = TileType.START
        tile.render(game_state, batch)
        self.assertEqual(1, len(batch.top_groups))
        self.assertEqual(pyglet.graphics.NullGroup, type(batch.top_groups[0]))

    def test_no_render(self):
        game_state = GameState()
        game_state.init("./tower_defense/res")
        game_state.window_size = Vector(100, 100)

        position = Vector(1, 1)
        size = Vector(10, 10)
        tile_type = TileType.BUILDING_GROUND
        tile = Tile(position, size, tile_type)

        batch = pyglet.graphics.Batch()
        tile.render(game_state, batch)
        self.assertEqual(0, len(batch.top_groups))

    def test_render_no_arrow(self):
        game_state = GameState()
        game_state.init("./tower_defense/res")
        game_state.window_size = Vector(100, 100)

        position = Vector(1, 1)
        size = Vector(10, 10)
        tile_type = TileType.BUILDING_GROUND
        tile = Tile(position, size, tile_type)

        batch = pyglet.graphics.Batch()
        tile.render_arrow(game_state, batch)
        self.assertEqual(0, len(batch.top_groups))

        tile.position = Vector()
        batch = pyglet.graphics.Batch()
        tile.render_arrow(game_state, batch)
        self.assertEqual(0, len(batch.top_groups))

    def test_render_arrow(self):
        game_state = GameState()
        game_state.init("./tower_defense/res")
        game_state.window_size = Vector(100, 100)

        position = Vector()
        size = Vector(10, 10)
        tile_type = TileType.BUILDING_GROUND
        tile = Tile(position, size, tile_type)
        tile.direction_index = 1
        tile.timer = 50

        tile.directions = [(1, 0)]
        batch = pyglet.graphics.Batch()
        tile.render_arrow(game_state, batch)
        self.assertEqual(1, len(batch.top_groups))
        self.assertEqual(pyglet.graphics.TextureGroup, type(batch.top_groups[0]))

        tile.directions = [(-1, 0)]
        batch = pyglet.graphics.Batch()
        tile.render_arrow(game_state, batch)
        self.assertEqual(1, len(batch.top_groups))
        self.assertEqual(pyglet.graphics.TextureGroup, type(batch.top_groups[0]))

        tile.directions = [(0, 1)]
        batch = pyglet.graphics.Batch()
        tile.render_arrow(game_state, batch)
        self.assertEqual(1, len(batch.top_groups))
        self.assertEqual(pyglet.graphics.TextureGroup, type(batch.top_groups[0]))

        tile.directions = [(0, -1)]
        batch = pyglet.graphics.Batch()
        tile.render_arrow(game_state, batch)
        self.assertEqual(1, len(batch.top_groups))
        self.assertEqual(pyglet.graphics.TextureGroup, type(batch.top_groups[0]))
