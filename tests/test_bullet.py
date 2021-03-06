import unittest

import pyglet

from tower_defense.entities.bullet import Bullet
from tower_defense.entities.entity import Entity
from tower_defense.game_state import GameState
from tower_defense.game_types import EntityType
from tower_defense.helper import Vector


class BulletTest(unittest.TestCase):
    def test_render(self):
        game_state = GameState()
        game_state.init("./tower_defense/res")
        game_state.window_size = Vector(100, 100)

        bullet = Bullet(Vector(), Vector(10, 10), Vector())
        batch = pyglet.graphics.Batch()
        bullet.render(game_state, batch)
        self.assertEqual(1, len(batch.top_groups))
        self.assertEqual(pyglet.graphics.TextureGroup, type(batch.top_groups[0]))

        bullet = Bullet(Vector(10, 10), Vector(10, 10), Vector())
        batch = pyglet.graphics.Batch()
        bullet.render(game_state, batch)
        self.assertEqual(0, len(batch.top_groups))

    def test_update(self):
        game_state = GameState()

        bullet = Bullet(Vector(), Vector(10, 10), Vector(1, 1))
        result = bullet.update(game_state)
        self.assertFalse(result)

        bullet = Bullet(Vector(), Vector(10, 10), Vector(-1, -1))
        result = bullet.update(game_state)
        self.assertTrue(result)

    def test_update_with_entity_hit(self):
        game_state = GameState()
        entity = Entity(Vector(0, 0), Vector(10, 10), EntityType.LARGE_BOULDER)
        game_state.entity_manager.entities = [entity]

        bullet = Bullet(Vector(), Vector(10, 10), Vector(1, 1))
        result = bullet.update(game_state)
        self.assertTrue(result)
