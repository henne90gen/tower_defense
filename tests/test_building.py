import unittest

import pyglet

from buildings.building import Building
from entities.entity import Entity
from game_state import GameState
from game_types import BuildingType
from helper import Vector


class BuildingTest(unittest.TestCase):
    def test_render(self):
        game_state = GameState()
        game_state.init("./tower_defense/res")
        game_state.window_size = Vector(100, 100)

        building = Building(Vector(1, 1), Vector(10, 10), BuildingType.LASER)
        batch = pyglet.graphics.Batch()
        building.render(game_state, batch)
        self.assertEqual(0, len(batch.top_groups))

        batch = pyglet.graphics.Batch()
        building = Building(Vector(), Vector(10, 10), BuildingType.LASER)
        building.mouse_over = True
        building.render(game_state, batch)
        self.assertEqual(1, len(batch.top_groups))
        self.assertEqual(pyglet.graphics.TextureGroup, type(batch.top_groups[0]))

    def test_range(self):
        building = Building(Vector(), Vector(10, 10), BuildingType.LASER)
        self.assertEqual(200, building.range)

        building = Building(Vector(), Vector(10, 10), BuildingType.CATAPULT)
        self.assertEqual(300, building.range)

    def test_shooting_frequency(self):
        building = Building(Vector(), Vector(10, 10), BuildingType.LASER)
        self.assertEqual(1 / 30, building.shooting_frequency)

        building = Building(Vector(), Vector(10, 10), BuildingType.CATAPULT)
        self.assertEqual(1 / 60, building.shooting_frequency)

    @unittest.skip("Make separate tests for all buildings")
    def test_update(self):
        was_called = []

        def shoot(*_):
            was_called.append(0)

        game_state = GameState()
        game_state.window_size = Vector(100, 100)
        game_state.building_manager.shoot = shoot

        # no enemy to shoot at
        building = Building(Vector(), Vector(10, 10), BuildingType.LASER)
        building.cool_down = 0
        building.update(game_state)
        self.assertEqual(0, len(was_called))

        # on cool down
        building = Building(Vector(), Vector(10, 10), BuildingType.LASER)
        building.cool_down = 100
        building.update(game_state)
        self.assertEqual(0, len(was_called))

        # shooting
        game_state.entity_manager.entities.append(Entity(Vector(150, 0), Vector(10, 10)))
        building = Building(Vector(), Vector(10, 10), BuildingType.LASER)
        building.cool_down = 0
        building.update(game_state)
        self.assertEqual(1, len(was_called))
