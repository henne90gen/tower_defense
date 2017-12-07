from typing import List, Dict

import pygame
import math

import pyglet

from game_types import EntityType, TileType
from helper import Vector


class Entity:
    def __init__(self, position: Vector, size: Vector):
        self.entity_type = EntityType.WARRIOR
        self.position = position
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
            for d in game_state.entity_manager.tiles[self.next_tile_index]:
                if min_d is None:
                    min_d = d
                elif min_d[1] > d[1]:
                    min_d = d
            if min_d:
                direction = min_d[0]
                index = game_state.entity_manager.tiles[self.next_tile_index].index(min_d)
                game_state.entity_manager.tiles[self.next_tile_index][index] = min_d[0], min_d[1] + 1
                self.next_tile_index = self.next_tile_index[0] + direction[0], self.next_tile_index[1] + direction[1]

        # calculate movement of entity
        tile = game_state.tile_map.tiles[self.next_tile_index]
        target = tile.world_position
        half_tile_size = tile.size / 2
        target = target + half_tile_size

        desired_velocity = target - self.position
        desired_speed = desired_velocity.length()
        desired_velocity = desired_velocity / desired_speed
        desired_velocity = desired_velocity * self.max_speed

        steer = desired_velocity - self.velocity

        self.acceleration = self.acceleration + steer
        self.velocity = self.velocity + self.acceleration
        self.position = self.position + self.velocity
        self.acceleration = (0, 0)

    def render(self, game_state, batch: pyglet.graphics.Batch):
        x, y = self.position.x, self.position.y
        x -= self.size.x / 2 - game_state.world_offset.x
        y -= self.size.y / 2 - game_state.world_offset.y

        top_left = Vector(x, y + self.size.y)
        bottom_right = Vector(top_left.x + self.size.x, top_left.y - self.size.y)
        vertices = [bottom_right.x, bottom_right.y,
                    bottom_right.x, top_left.y,
                    top_left.x, top_left.y,
                    top_left.x, bottom_right.y]

        texture_coords = [1, 0.0,
                          1, 1,
                          0.0, 1,
                          0.0, 0.0]
        batch.add(4, pyglet.graphics.GL_QUADS, game_state.textures.entities[self.entity_type], ('v2f/static', vertices),
                  ('t2f/static', texture_coords))


class EntityManager:
    def __init__(self):
        self.entities: List[Entity] = []
        # holds a dictionary similar to the one in TileMap, the only difference being that this one doesn't have tiles
        # as values, but rather a list with the directions associated with that tile and a counter with each direction
        # The counter indicates how many time a certain direction has been taken already
        self.directions_graph: Dict[(int, int), List[((int, int), int)]] = None
        self.spawn_timer = 0

    def render(self, game_state):
        batch = pyglet.graphics.Batch()
        for entity in self.entities:
            entity.render(game_state, batch)
        batch.draw()

    def spawn_random_entity(self, position: Vector):
        entity = Entity(position, Vector(100, 100))
        self.entities.append(entity)

    def update(self, game_state):
        # initialize tiles
        if self.directions_graph is None:
            self.directions_graph = {}
            for tile in game_state.tile_map.tiles:
                self.directions_graph[tile] = []
                for direction in game_state.tile_map.tiles[tile].directions:
                    self.directions_graph[tile].append((direction, 0))

        for entity in self.entities.copy():
            entity.update(game_state)
            tile_index = game_state.tile_map.get_tile_index(entity.position)
            if game_state.tile_map.tiles[tile_index].tile_type == TileType.FINISH:
                self.entities.remove(entity)

        if not game_state.entity_placement_mode:
            return

        self.spawn_timer += 1
        for tile_index in game_state.tile_map.tiles:
            tile = game_state.tile_map.tiles[tile_index]
            if tile.tile_type == TileType.START and self.spawn_timer > 15:
                self.spawn_timer = 0
                self.spawn_random_entity(tile.world_position + (tile.size / 2))
                break

        for click in game_state.mouse_clicks.copy():
            position = game_state.to_tile_map_space(click.position)

            if game_state.tile_map.is_on_map(game_state, position):
                tile_index = game_state.tile_map.get_tile_index(position)
                if game_state.tile_map.tiles[tile_index].is_walkable:
                    self.spawn_random_entity(position)
                    game_state.mouse_clicks.remove(click)
