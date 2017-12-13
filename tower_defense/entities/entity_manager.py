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
        self.spawn_timer = 0

    def render(self, game_state):
        batch = pyglet.graphics.Batch()
        for entity in self.entities:
            entity.render(game_state, batch)
        batch.draw()

    def reset(self):
        self.directions_graph = {}
        self.entities = []
        self.spawn_timer = 0

    def spawn_random_entity(self, position: Vector):
        entity = Entity(position, Vector(100, 100))
        self.entities.append(entity)

    def update(self, game_state):
        # initialize directions graph
        for tile in game_state.tile_map.tiles:
            if tile not in self.directions_graph:
                self.directions_graph[tile] = {}
            for direction in self.directions_graph[tile].copy():
                if direction not in game_state.tile_map.tiles[tile].directions:
                    del self.directions_graph[tile][direction]
            for direction in game_state.tile_map.tiles[tile].directions:
                if direction not in self.directions_graph[tile]:
                    self.directions_graph[tile][direction] = 0

        for entity in self.entities.copy():
            entity.update(game_state)
            tile_index = game_state.world_to_index_space(entity.position)
            if game_state.tile_map.tiles[tile_index].tile_type == TileType.FINISH:
                game_state.player_health -= entity.player_damage
                self.entities.remove(entity)
            if entity.health <= 0:
                self.entities.remove(entity)

        if not game_state.test_mode:
            return

        self.spawn_timer += 1
        for tile_index in game_state.tile_map.tiles:
            tile = game_state.tile_map.tiles[tile_index]
            if tile.tile_type == TileType.START and self.spawn_timer > 60:
                self.spawn_timer = 0
                self.spawn_random_entity(tile.world_position + (tile.size / 2))
                break
