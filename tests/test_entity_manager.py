import unittest

from entities.entity import Entity
from entities.entity_manager import EntityManager, EditorEntityManager
from game_state import GameState
from game_types import GameMode, TileType
from helper import Vector


class EntityManagerTest(unittest.TestCase):
    def test_render(self):
        game_state = GameState()
        was_called = []

        def render(game_state, batch):
            was_called.append(0)

        position = Vector()
        size = Vector()
        entity = Entity(position, size)
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
        entity_manager = EntityManager()
        position = Vector(1, 1)
        entity_manager.spawn_random_entity(position)
        self.assertEqual(1, len(entity_manager.entities))
        self.assertEqual(position, entity_manager.entities[0].position)

    def test_update_entities(self):
        game_state = GameState()
        was_called = []

        def update(game_state):
            was_called.append(0)

        entity = Entity(Vector(), Vector())
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
        entity_manager.entities = [entity]
        entity_manager.update_entities(game_state)
        self.assertEqual(0, len(entity_manager.entities))

    @unittest.skip("Implement this")
    def test_generate_directions_graph(self):
        self.fail()


class EditorEntityManagerTest(unittest.TestCase):
    def test_update(self):
        game_state = GameState()
        game_state.tile_map.tiles[(0, 0)].tile_type = TileType.START
        game_state.tile_map.tiles[(1, 1)].tile_type = TileType.FINISH
        entity_manager = EditorEntityManager()
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
        entity_manager.update(game_state)
        self.assertEqual(1, len(entity_manager.entities))
        self.assertEqual(0, entity_manager.spawn_timer)

    def test_update_reset_spawn_timer(self):
        game_state = GameState()
        entity_manager = EditorEntityManager()
        game_state.entity_manager = entity_manager

        entity_manager.spawn_timer = 60
        entity_manager.update(game_state)
        self.assertEqual(0, len(entity_manager.entities))
        self.assertEqual(0, entity_manager.spawn_timer)

    def test_reset(self):
        entity_manager = EditorEntityManager()
        entity_manager.reset()
        self.assertEqual(0, entity_manager.spawn_timer)
