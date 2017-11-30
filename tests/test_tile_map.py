from unittest import TestCase

from tile_map import TileMap, Tile, TileType


class TileMapTest(TestCase):
    def test_init_tiles(self):
        # expected = [
        #     Tile(), Tile(),
        #     Tile(), Tile()
        # ]
        # actual = TileMap.init_tiles(2, 2, 100, 100)

        # self.assertListEqual(expected, actual)
        pass

    def test_tile_type(self):
        items = list(TileType.__members__.values()).index(TileType.BALL)
        print(items)
        print(TileType(0))
