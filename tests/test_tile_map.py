from unittest import TestCase

from game_types import TileType
from helper import Vector
from tile_map import Tile, TileMap


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

    def test_tile_type(self):
        # items = list(TileType.__members__.values()).index(TileType.BALL)
        # print(items)
        # print(TileType(0))
        pass
