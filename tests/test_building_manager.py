import unittest

from tower_defense.buildings.building import Laser, Drill, Hammer, Building
from tower_defense.buildings.building_manager import BuildingManager
from tower_defense.game_state import GameState
from tower_defense.game_types import BuildingType
from tower_defense.helper import Vector, MouseClick


class Object(object):
    pass


class BuildingManagerTest(unittest.TestCase):
    def test_update(self):
        game_state = GameState()
        was_called = []

        def dummy(*_):
            was_called.append(0)
            return True

        building = Object()
        building.update = dummy

        bullet = Object()
        bullet.update = dummy

        building_manager = BuildingManager()
        building_manager.buildings = {'building': building}
        building_manager.bullets = [bullet]
        building_manager.update(game_state)
        self.assertEqual(2, len(was_called))
        self.assertEqual(0, len(building_manager.bullets))
        self.assertEqual(1, len(building_manager.buildings))

    def test_render(self):
        game_state = GameState()
        was_called = []

        def dummy(*_, **kwargs):
            was_called.append(0)

        building = Object()
        building.render = dummy

        bullet = Object()
        bullet.render = dummy

        building_manager = BuildingManager()
        building_manager.buildings = {'building': building}
        building_manager.bullets = [bullet]
        building_manager.render(game_state)
        self.assertEqual(2, len(was_called))

    def test_shoot(self):
        building_manager = BuildingManager()
        world_position = Vector()
        direction = Vector(1, 0)
        building_manager.shoot(world_position, direction)
        self.assertEqual(1, len(building_manager.bullets))
        bullet = building_manager.bullets[0]
        self.assertEqual(world_position, bullet.position)
        self.assertEqual(direction * 5, bullet.velocity)

    def test_spawn_building(self):
        game_state = GameState()
        tile_index = (1, 0)

        building_manager = BuildingManager()
        building_manager.spawn_building(game_state, tile_index, BuildingType.LASER)
        self.assertEqual(1, len(building_manager.buildings))
        self.assertEqual((1, 0), list(building_manager.buildings.keys())[0])

        building = building_manager.buildings[(1, 0)]
        self.assertEqual(Vector(1, 0), building.position)
        self.assertEqual(Laser, type(building))

        building_manager.spawn_building(game_state, tile_index, BuildingType.DRILL)
        self.assertEqual(Drill, type(building_manager.buildings[(1, 0)]))

        building_manager.spawn_building(game_state, tile_index, BuildingType.HAMMER)
        self.assertEqual(Hammer, type(building_manager.buildings[(1, 0)]))

        building_manager.spawn_building(game_state, tile_index, -1)
        self.assertEqual(Building, type(building_manager.buildings[(1, 0)]))

        building_manager = BuildingManager()
        building_manager.gold = 0
        building_manager.spawn_building(game_state, tile_index, BuildingType.HAMMER)
        self.assertEqual(0, len(building_manager.buildings.keys()))
