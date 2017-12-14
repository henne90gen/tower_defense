import unittest

import pyglet

from buildings.building import Building
from entities.entity import Entity
from game_state import GameState
from helper import Vector


class BuildingTest(unittest.TestCase):
    def test_render(self):
        game_state = GameState()
        game_state.init("./tower_defense/res")
        game_state.window_size = Vector(100, 100)

        building = Building(Vector(), Vector(10, 10))
        batch = pyglet.graphics.Batch()
        building.render(game_state, batch)
        self.assertEqual(1, len(batch.top_groups))
        self.assertEqual(pyglet.graphics.TextureGroup, type(batch.top_groups[0]))

        building = Building(Vector(1, 1), Vector(10, 10))
        batch = pyglet.graphics.Batch()
        building.render(game_state, batch)
        self.assertEqual(0, len(batch.top_groups))

    def test_range(self):
        building = Building(Vector(), Vector(10, 10))
        self.assertEqual(200, building.range)

    def test_update_on_cooldown(self):
        was_called = []

        def shoot(position, direction):
            was_called.append(0)

        game_state = GameState()
        game_state.building_manager.shoot = shoot
        building = Building(Vector(), Vector(10, 10))
        building.cool_down = 100
        building.update(game_state)
        self.assertEqual(0, len(was_called))

    def test_update_nothing_in_range(self):
        was_called = []

        def shoot(position, direction):
            was_called.append(0)

        game_state = GameState()
        game_state.building_manager.shoot = shoot
        building = Building(Vector(), Vector(10, 10))
        building.cool_down = 0
        building.update(game_state)
        self.assertEqual(0, len(was_called))

    def test_update(self):
        was_called = []

        def shoot(position, direction):
            was_called.append(0)

        game_state = GameState()
        game_state.building_manager.shoot = shoot
        game_state.entity_manager.entities.append(Entity(Vector(150, 0), Vector(10, 10)))
        building = Building(Vector(), Vector(10, 10))
        building.cool_down = 0
        building.update(game_state)
        self.assertEqual(1, len(was_called))
