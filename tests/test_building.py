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

        building = Building(Vector(), Vector(10, 10), BuildingType.Archer)
        batch = pyglet.graphics.Batch()
        building.render(game_state, batch)
        self.assertEqual(1, len(batch.top_groups))
        self.assertEqual(pyglet.graphics.TextureGroup, type(batch.top_groups[0]))

        building = Building(Vector(1, 1), Vector(10, 10), BuildingType.Archer)
        batch = pyglet.graphics.Batch()
        building.render(game_state, batch)
        self.assertEqual(0, len(batch.top_groups))

    def test_range(self):
        building = Building(Vector(), Vector(10, 10), BuildingType.Archer)
        self.assertEqual(200, building.range)

    def test_update(self):
        was_called = []

        def shoot(*_):
            was_called.append(0)

        game_state = GameState()
        game_state.window_size = Vector(100, 100)
        game_state.building_manager.shoot = shoot

        # no enemy to shoot at
        building = Building(Vector(), Vector(10, 10), BuildingType.Archer)
        building.cool_down = 0
        building.update(game_state)
        self.assertEqual(0, len(was_called))

        # on cool down
        building = Building(Vector(), Vector(10, 10), BuildingType.Archer)
        building.cool_down = 100
        building.update(game_state)
        self.assertEqual(0, len(was_called))

        # shooting
        game_state.entity_manager.entities.append(Entity(Vector(150, 0), Vector(10, 10)))
        building = Building(Vector(), Vector(10, 10), BuildingType.Archer)
        building.cool_down = 0
        building.update(game_state)
        self.assertEqual(1, len(was_called))
