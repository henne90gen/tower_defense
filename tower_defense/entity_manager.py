from typing import List, Dict

import pyglet

from game_types import EntityType, TileType
from graphics import render_textured_rectangle
from helper import Vector


class Entity:
    def __init__(self, position: Vector, size: Vector):
        self.entity_type = EntityType.WARRIOR
        self.position = position  # center of sprite
        self.size = size
        self.velocity = Vector()
        self.acceleration = Vector()
        self.max_speed = 2
        self.next_tile_index = None

    def update(self, game_state):
        tile_index = game_state.tile_map.get_tile_index(self.position)
        tile = game_state.tile_map.tiles[tile_index]
        if not tile:
            return
        if len(tile.directions) == 0:
            return
        if self.next_tile_index is None:
            self.next_tile_index = game_state.tile_map.get_tile_index(self.position)

        # update next tile to walk to
        if game_state.tile_map.get_tile_index(self.position) == self.next_tile_index:
            min_d = None
            for d in game_state.entity_manager.directions_graph[self.next_tile_index]:
                if min_d is None:
                    min_d = d, game_state.entity_manager.directions_graph[self.next_tile_index][d]
                elif min_d[1] > game_state.entity_manager.directions_graph[self.next_tile_index][d]:
                    min_d = d, game_state.entity_manager.directions_graph[self.next_tile_index][d]
            if min_d:
                direction = min_d[0]
                game_state.entity_manager.directions_graph[self.next_tile_index][direction] = min_d[1] + 1

                self.next_tile_index = self.next_tile_index[0] + direction[0], self.next_tile_index[1] + direction[1]

        # calculate movement of entity
        tile = game_state.tile_map.tiles[self.next_tile_index]
        target = tile.world_position
        half_tile_size = tile.size / 2
        target += half_tile_size

        desired_velocity = target - self.position
        desired_speed = desired_velocity.length()
        desired_velocity /= desired_speed
        desired_velocity *= self.max_speed

        steer = desired_velocity - self.velocity

        self.acceleration += steer
        self.velocity += self.acceleration
        self.position += self.velocity
        self.acceleration = (0, 0)

    def render(self, game_state, batch: pyglet.graphics.Batch):
        x, y = self.position.x, self.position.y
        x -= self.size.x / 2 - game_state.world_offset.x
        y -= self.size.y / 2 - game_state.world_offset.y

        render_textured_rectangle(batch, game_state.textures.entities[self.entity_type], Vector(x, y), self.size)

    def take_damage(self, damage):
        print("Took", damage, "damage")


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
            tile_index = game_state.tile_map.get_tile_index(entity.position)
            if game_state.tile_map.tiles[tile_index].tile_type == TileType.FINISH:
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
