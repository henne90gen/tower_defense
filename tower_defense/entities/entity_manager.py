from typing import List, Dict

import pyglet

from entities.entity import Entity
from game_types import TileType
from helper import Vector


class EntityManager:
    def __init__(self):
        self.entities: List[Entity] = []
        # holds a dictionary similar to the one in TileMap, the only difference being that this one doesn't have tiles
        # as values, but rather a list with the directions associated with that tile and a counter with each direction
        # The counter indicates how many time a certain direction has been taken already
        self.directions_graph: Dict[(int, int), List[((int, int), int)]] = {}

    def render(self, game_state):
        batch = pyglet.graphics.Batch()
        for entity in self.entities:
            entity.render(game_state, batch)
        batch.draw()

    def reset(self):
        self.directions_graph = {}
        self.entities = []

    def spawn_random_entity(self, position: Vector):
        entity = Entity(position, Vector(100, 100))
        self.entities.append(entity)

    def update(self, game_state):
        self.generate_directions_graph(game_state)
        self.update_entities(game_state)

    def next_wave(self):
        pass

    def update_entities(self, game_state):
        for entity in self.entities.copy():
            entity.update(game_state)
            tile_index = game_state.world_to_index_space(entity.position)
            if game_state.tile_map.tiles[tile_index].tile_type == TileType.FINISH:
                game_state.player_health -= entity.player_damage
                self.entities.remove(entity)
            elif entity.health <= 0:
                self.entities.remove(entity)

    def generate_directions_graph(self, game_state):
        for tile in game_state.tile_map.tiles:
            if tile not in self.directions_graph:
                self.directions_graph[tile] = {}

            for direction in self.directions_graph[tile].copy():
                if direction not in game_state.tile_map.tiles[tile].directions:
                    del self.directions_graph[tile][direction]

            for direction in game_state.tile_map.tiles[tile].directions:
                if direction not in self.directions_graph[tile]:
                    self.directions_graph[tile][direction] = 0


class EditorEntityManager(EntityManager):
    def __init__(self):
        super().__init__()
        self.spawn_timer = 0
        self.should_spawn = True

    def update(self, game_state):
        super().update(game_state)

        if not self.should_spawn:
            return

        self.spawn_timer += 1
        if self.spawn_timer < 60:
            return

        self.spawn_timer = 0
        for tile_index in game_state.tile_map.tiles:
            tile = game_state.tile_map.tiles[tile_index]
            if tile.tile_type == TileType.START and game_state.tile_map.has_finish_node:
                self.spawn_random_entity(tile.world_position + (tile.size / 2))
                break

    def reset(self):
        super().reset()
        self.spawn_timer = 0


class GameEntityManager(EntityManager):
    def __init__(self):
        super().__init__()
        self.wave_count = 0
        self.wave = []

    @property
    def wave_running(self):
        return len(self.wave) > 0

    def next_wave(self):
        self.wave_count += 1
        # TODO init next wave
        self.wave = [1]
