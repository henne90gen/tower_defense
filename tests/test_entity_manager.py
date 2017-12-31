import unittest

from entities.entity import Entity
from entities.entity_manager import EntityManager, EditorEntityManager, GameEntityManager
from game_state import GameState
from game_types import TileType, EntityType
from helper import Vector


class EntityManagerTest(unittest.TestCase):
    @staticmethod
    def test_next_wave():
        entity_manager = EntityManager()
        entity_manager.next_wave()

    def test_render(self):
        game_state = GameState()
        was_called = []

        def render(*_):
            was_called.append(0)

        position = Vector()
        size = Vector()
        entity = Entity(position, size, EntityType.LARGE_BOULDER)
        entity.render = render

        entity_manager = EntityManager()
        entity_manager.entities = [entity]
        entity_manager.render(game_state)
        self.assertEqual(1, len(was_called))

    def test_reset(self):
        entity_manager = EntityManager()
        entity_manager.entities = ["entity"]
        entity_manager.spawn_timer = 1
        entity_manager.directions_graph = {"key": "value"}
        entity_manager.reset()
        self.assertEqual({}, entity_manager.directions_graph)
        self.assertEqual([], entity_manager.entities)

    def test_spawn_random_entity(self):
        game_state = GameState()
        game_state.tile_map.tiles[(0, 0)].tile_type = TileType.START
        game_state.tile_map.tiles[(1, 0)].tile_type = TileType.FINISH

        entity_manager = EntityManager()
        entity_manager.spawn_entity(game_state, EntityType.LARGE_BOULDER)
        self.assertEqual(1, len(entity_manager.entities))
        self.assertEqual(Vector(50, 50), entity_manager.entities[0].position)

    def test_update_entities(self):
        game_state = GameState()
        was_called = []

        def update(*_):
            was_called.append(0)

        entity = Entity(Vector(), Vector(), EntityType.LARGE_BOULDER)
        entity.update = update

        entity_manager = EntityManager()
        entity_manager.entities = [entity]
        entity_manager.update_entities(game_state)

        self.assertEqual(1, len(was_called))

        before_health = game_state.player_health
        game_state.tile_map.tiles[(0, 0)].tile_type = TileType.FINISH
        entity_manager.entities = [entity]
        entity_manager.update_entities(game_state)
        self.assertEqual(0, len(entity_manager.entities))
        self.assertEqual(before_health - 1, game_state.player_health)

        game_state = GameState()
        entity.health = 0
        entity.entity_type = EntityType.SMALL_BOULDER
        entity_manager.entities = [entity]
        entity_manager.update_entities(game_state)
        self.assertEqual(0, len(entity_manager.entities))

    def test_update_split_large_boulder(self):
        game_state = GameState()
        entity = Entity(Vector(), Vector(), EntityType.LARGE_BOULDER)
        entity.health = 0
        entity_manager = EntityManager()
        entity_manager.entities = [entity]
        entity_manager.update_entities(game_state)
        self.assertEqual(2, len(entity_manager.entities))

    @unittest.skip("Implement this")
    def test_generate_directions_graph(self):
        self.fail()


class EditorEntityManagerTest(unittest.TestCase):
    def test_update(self):
        game_state = GameState()
        game_state.tile_map.tiles[(0, 0)].tile_type = TileType.START
        game_state.tile_map.tiles[(1, 1)].tile_type = TileType.FINISH
        entity_manager = EditorEntityManager()
        entity_manager.spawn_timer = 0
        game_state.entity_manager = entity_manager

        entity_manager.update(game_state)
        self.assertEqual(0, len(entity_manager.entities))
        self.assertEqual(1, entity_manager.spawn_timer)

    def test_update_spawn_entity(self):
        game_state = GameState()
        game_state.tile_map.tiles[(0, 0)].tile_type = TileType.START
        game_state.tile_map.tiles[(1, 1)].tile_type = TileType.FINISH
        entity_manager = EditorEntityManager()
        game_state.entity_manager = entity_manager

        game_state.tile_map.tiles[(0, 0)].tile_type = TileType.START
        entity_manager.spawn_timer = 60
        entity_manager.spawn_delay = 60
        entity_manager.update(game_state)
        self.assertEqual(1, len(entity_manager.entities))
        self.assertEqual(0, entity_manager.spawn_timer)

    def test_update_reset_spawn_timer(self):
        game_state = GameState()
        game_state.tile_map.tiles[(0, 0)].tile_type = TileType.FINISH

        entity_manager = EditorEntityManager()
        game_state.entity_manager = entity_manager

        entity_manager.spawn_timer = 60
        entity_manager.spawn_delay = 60
        entity_manager.update(game_state)
        self.assertEqual(1, len(entity_manager.entities))
        self.assertEqual(0, entity_manager.spawn_timer)

    def test_reset(self):
        entity_manager = EditorEntityManager()
        entity_manager.reset()
        self.assertEqual(0, entity_manager.spawn_timer)


class GameEntityManagerTest(unittest.TestCase):
    def test_wave_running(self):
        entity_manager = GameEntityManager()
        self.assertFalse(entity_manager.wave_running)

        entity_manager = GameEntityManager()
        entity_manager.wave = [0]
        self.assertTrue(entity_manager.wave_running)

    def test_next_wave(self):
        entity_manager = GameEntityManager()
        entity_manager.next_wave()
        self.assertTrue(entity_manager.wave_running)
        self.assertEqual(1, entity_manager.wave_count)
