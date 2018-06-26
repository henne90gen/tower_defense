import unittest

import pyglet

from tower_defense.entities.entity import Entity
from tower_defense.game_state import GameState
from tower_defense.game_types import TileType, EntityType
from tower_defense.helper import Vector


class EntityTest(unittest.TestCase):
    @staticmethod
    def test_update_cancel():
        game_state = GameState()

        entity = Entity(Vector(-100, -100), Vector(10, 10), EntityType.LARGE_BOULDER)
        entity.update(game_state)

        entity = Entity(Vector(1, 1), Vector(10, 10), EntityType.LARGE_BOULDER)
        entity.update(game_state)

    def test_update(self):
        game_state = GameState()
        game_state.tile_map.tiles[(0, 0)].tile_type = TileType.PATH
        game_state.tile_map.tiles[(0, 0)].directions = [(1, 0)]
        game_state.entity_manager.update(game_state)
        entity = Entity(Vector(1, 1), Vector(10, 10), EntityType.LARGE_BOULDER)
        entity.update(game_state)
        self.assertEqual((1, 0), entity.next_tile_index)

    def test_calculate_movement(self):
        game_state = GameState()

        entity = Entity(Vector(50, 50), Vector(10, 10), EntityType.LARGE_BOULDER)
        entity.next_tile_index = (1, 0)
        entity.calculate_movement(game_state)
        self.assertEqual(Vector(2, 0), entity.velocity, str(entity.velocity))
        self.assertEqual(Vector(52, 50), entity.position, str(entity.position))

    def test_render(self):
        game_state = GameState()
        game_state.init("./tower_defense/res")
        game_state.window_size = Vector(100, 100)

        entity = Entity(Vector(1, 1), Vector(10, 10), EntityType.LARGE_BOULDER)
        batch = pyglet.graphics.Batch()
        entity.render(game_state, batch)
        self.assertEqual(1, len(batch.top_groups))
        self.assertEqual(pyglet.graphics.TextureGroup, type(batch.top_groups[0]))

        entity = Entity(Vector(10, 10), Vector(10, 10), EntityType.LARGE_BOULDER)
        batch = pyglet.graphics.Batch()
        entity.render(game_state, batch)
        self.assertEqual(0, len(batch.top_groups))

    def test_take_damage(self):
        entity = Entity(Vector(), Vector(), EntityType.LARGE_BOULDER)
        entity.take_damage(10)
        self.assertEqual(90, entity.health)
