import unittest

import pyglet

from buildings.bullet import Bullet
from game_state import GameState
from helper import Vector


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
        pass
