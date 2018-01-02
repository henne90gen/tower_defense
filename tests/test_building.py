import unittest

import pyglet

from buildings.building import Building, Laser, Catapult, Drill
from entities.entity import Entity
from game_state import GameState
from game_types import BuildingType, EntityType, TileType
from graphics import MovementGroup
from helper import Vector


class BuildingTest(unittest.TestCase):
    def test_render(self):
        game_state = GameState()
        game_state.init("./tower_defense/res")
        game_state.window_size = Vector(100, 100)

        building = Building(Vector(20, 20), Vector(10, 10), BuildingType.LASER)
        batch = pyglet.graphics.Batch()
        building.render(game_state, batch)
        self.assertEqual(0, len(batch.top_groups))

        building = Building(Vector(), Vector(10, 10), BuildingType.LASER)
        batch = pyglet.graphics.Batch()
        building.render(game_state, batch)
        self.assertEqual(0, len(batch.top_groups))
        # self.assertEqual(pyglet.graphics.TextureGroup, type(batch.top_groups[0]))

        batch = pyglet.graphics.Batch()
        building = Building(Vector(), Vector(10, 10), BuildingType.LASER)
        building.mouse_over = True
        building.render(game_state, batch)
        self.assertEqual(1, len(batch.top_groups))
        self.assertEqual(pyglet.graphics.TextureGroup, type(batch.top_groups[0]))
        # self.assertEqual(pyglet.graphics.TextureGroup, type(batch.top_groups[1]))

    def test_range(self):
        building = Building(Vector(), Vector(10, 10), BuildingType.LASER)
        self.assertEqual(350, building.range)

        building = Building(Vector(), Vector(10, 10), BuildingType.CATAPULT)
        self.assertEqual(300, building.range)

        building = Building(Vector(), Vector(10, 10), BuildingType.DRILL)
        self.assertEqual(150, building.range)

        building = Building(Vector(), Vector(10, 10), -1)
        self.assertEqual(-1, building.range)

    def test_cost(self):
        building = Building(Vector(), Vector(10, 10), BuildingType.LASER)
        self.assertEqual(20, building.cost)

        building = Building(Vector(), Vector(10, 10), BuildingType.CATAPULT)
        self.assertEqual(50, building.cost)

        building = Building(Vector(), Vector(10, 10), BuildingType.DRILL)
        self.assertEqual(30, building.cost)

        building = Building(Vector(), Vector(10, 10), -1)
        self.assertEqual(-1, building.cost)

    def test_shooting_frequency(self):
        building = Building(Vector(), Vector(10, 10), BuildingType.LASER)
        self.assertEqual(1 / 30, building.shooting_frequency)

        building = Building(Vector(), Vector(10, 10), BuildingType.CATAPULT)
        self.assertEqual(1 / 60, building.shooting_frequency)


class LaserTest(unittest.TestCase):
    def test_render(self):
        game_state = GameState()
        game_state.init("./tower_defense/res")
        game_state.window_size = Vector(100, 100)

        building = Laser(Vector(), Vector(10, 10))
        batch = pyglet.graphics.Batch()
        building.render(game_state, batch)
        self.assertEqual(1, len(batch.top_groups))
        self.assertEqual(pyglet.graphics.TextureGroup, type(batch.top_groups[0]))

        building = Laser(Vector(20, 20), Vector(10, 10))
        batch = pyglet.graphics.Batch()
        building.render(game_state, batch)
        self.assertEqual(0, len(batch.top_groups))


@unittest.skip("Implement this")
class CatapultTest(unittest.TestCase):
    def test_render(self):
        game_state = GameState()
        game_state.init("./tower_defense/res")
        game_state.window_size = Vector(100, 100)

        building = Catapult(Vector(), Vector(10, 10))
        batch = pyglet.graphics.Batch()
        building.render(game_state, batch)
        self.assertEqual(1, len(batch.top_groups))
        self.assertEqual(pyglet.graphics.TextureGroup, type(batch.top_groups[0]))

        building = Catapult(Vector(20, 20), Vector(10, 10))
        batch = pyglet.graphics.Batch()
        building.render(game_state, batch)
        self.assertEqual(0, len(batch.top_groups))

    def test_update(self):
        was_called = []

        def shoot(*_):
            was_called.append(0)

        game_state = GameState()
        game_state.window_size = Vector(100, 100)
        game_state.building_manager.shoot = shoot

        # no enemy to shoot at
        building = Laser(Vector(), Vector(10, 10))
        building.cool_down = 0
        building.update(game_state)
        self.assertEqual(0, len(was_called))

        # on cool down
        building = Laser(Vector(), Vector(10, 10))
        building.cool_down = 100
        building.update(game_state)
        self.assertEqual(0, len(was_called))

        # shooting
        game_state.entity_manager.entities = [Entity(Vector(150, 0), Vector(10, 10), EntityType.LARGE_BOULDER)]
        building = Laser(Vector(), Vector(10, 10))
        building.cool_down = 0
        building.update(game_state)
        self.assertEqual(1, len(was_called))


class DrillTest(unittest.TestCase):
    def test_rotate_towards(self):
        building = Drill(Vector(), Vector(10, 10))
        building.rotate_towards(10)
        self.assertEqual(2, building.rotation_angle)

    def test_render(self):
        game_state = GameState()
        game_state.init("./tower_defense/res")
        game_state.window_size = Vector(100, 100)

        building = Drill(Vector(20, 20), Vector(10, 10))
        batch = pyglet.graphics.Batch()
        building.render(game_state, batch)
        self.assertEqual(0, len(batch.top_groups))

        building = Drill(Vector(), Vector(10, 10))
        batch = pyglet.graphics.Batch()
        building.render(game_state, batch)
        self.assertEqual(2, len(batch.top_groups))
        self.assertEqual(pyglet.graphics.TextureGroup, type(batch.top_groups[0]))
        self.assertEqual(MovementGroup, type(batch.top_groups[1]))

    def test_update_reset_animation_speed(self):
        game_state = GameState()
        game_state.window_size = Vector(100, 100)

        building = Drill(Vector(), Vector(10, 10))
        building.animation_speed = 5
        building.update(game_state)
        self.assertEqual(0, building.animation_speed)

    def test_update_animation_angle(self):
        game_state = GameState()
        game_state.window_size = Vector(100, 100)

        building = Drill(Vector(), Vector(10, 10))
        building.animation_speed = 5
        building.update(game_state)
        self.assertEqual(5, building.animation_angle)

        building = Drill(Vector(), Vector(10, 10))
        building.animation_speed = 5
        building.animation_angle = 356
        building.update(game_state)
        self.assertEqual(0, building.animation_angle)

    def test_check_for_entities(self):
        game_state = GameState()
        game_state.window_size = Vector(100, 100)

        building = Drill(Vector(), Vector(10, 10))
        result = building.check_for_entities(game_state)
        self.assertEqual(False, result)

        game_state = GameState()
        game_state.window_size = Vector(100, 100)
        game_state.entity_manager.entities = [Entity(Vector(), Vector(10, 10), EntityType.LARGE_BOULDER)]

        building = Drill(Vector(), Vector(10, 10))
        result = building.check_for_entities(game_state)
        self.assertEqual(True, result)
        self.assertEqual(5, building.animation_speed)
        self.assertEqual(99, game_state.entity_manager.entities[0].health)

    def test_closest_tile_angle(self):
        game_state = GameState()
        building = Drill(Vector(1, 1), Vector(10, 10))
        actual = building.closest_tile_angle(game_state)
        self.assertEqual(0, actual)

        game_state = GameState()
        game_state.tile_map.tiles[(1, 0)].tile_type = TileType.PATH
        actual = building.closest_tile_angle(game_state)
        self.assertEqual(0, actual)

        game_state = GameState()
        game_state.tile_map.tiles[(0, 1)].tile_type = TileType.PATH
        actual = building.closest_tile_angle(game_state)
        self.assertEqual(-90, actual)

        game_state = GameState()
        game_state.tile_map.tiles[(1, 2)].tile_type = TileType.PATH
        actual = building.closest_tile_angle(game_state)
        self.assertEqual(180, actual)

        game_state = GameState()
        game_state.tile_map.tiles[(2, 1)].tile_type = TileType.PATH
        actual = building.closest_tile_angle(game_state)
        self.assertEqual(90, actual)
