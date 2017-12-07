from typing import List, Dict

import pygame
import math
from game_types import EntityType, TileType


class Entity:
    def __init__(self, position: (int, int)):
        self.entity_type = EntityType.WARRIOR
        self.position = position
        self.velocity = (0, 0)
        self.acceleration = (0, 0)
        self.max_speed = 2
        self.next_tile = None

    def update(self, game_state):
        tile = game_state.tile_map.get_tile(game_state, self.position)
        if not tile:
            return
        if len(tile.directions) == 0:
            return
        if self.next_tile is None:
            self.next_tile = game_state.tile_map.get_tile_index(self.position)

        # update next tile to walk to
        if game_state.tile_map.get_tile_index(self.position) == self.next_tile:
            min_d = None
            for d in game_state.entity_manager.tiles[self.next_tile]:
                if min_d is None:
                    min_d = d
                elif min_d[1] > d[1]:
                    min_d = d
            direction = min_d[0]
            index = game_state.entity_manager.tiles[self.next_tile].index(min_d)
            game_state.entity_manager.tiles[self.next_tile][index] = min_d[0], min_d[1] + 1
            self.next_tile = self.next_tile[0] + direction[0], self.next_tile[1] + direction[1]

        # calculate movement of entity
        rect = game_state.tile_map.tiles[self.next_tile].rect
        target_x, target_y = rect.left, rect.top
        target_x += rect.width / 2
        target_y += rect.height / 2

        des_vel_x, des_vel_y = target_x - self.position[0], target_y - self.position[1]
        desired_speed = math.sqrt(des_vel_x * des_vel_x + des_vel_y * des_vel_y)
        desired_velocity = des_vel_x / desired_speed * self.max_speed, des_vel_y / desired_speed * self.max_speed

        steer = desired_velocity[0] - self.velocity[0], desired_velocity[1] - self.velocity[1]

        self.acceleration = self.acceleration[0] + steer[0], self.acceleration[1] + steer[1]
        self.velocity = self.velocity[0] + self.acceleration[0], self.velocity[1] + self.acceleration[1]
        self.position = self.position[0] + self.velocity[0], self.position[1] + self.velocity[1]
        self.acceleration = (0, 0)

    def render(self, game_state, screen: pygame.Surface):
        texture = game_state.textures.entities[self.entity_type]
        x, y = self.position
        x -= texture.get_width() / 2 - game_state.world_offset_x
        y -= texture.get_height() / 2 - game_state.world_offset_y
        screen.blit(texture, (x, y))


class EntityManager:
    def __init__(self):
        self.entities: List[Entity] = []
        self.tiles: Dict[(int, int), List[((int, int), int)]] = None

    def render(self, game_state, screen: pygame.Surface):
        for entity in self.entities:
            entity.render(game_state, screen)

    def spawn_random_entity(self, position: (int, int)):
        entity = Entity(position)
        self.entities.append(entity)

    def update(self, game_state):
        # initialize tiles
        if self.tiles is None:
            self.tiles = {}
            for tile in game_state.tile_map.tiles:
                self.tiles[tile] = []
                for direction in game_state.tile_map.tiles[tile].directions:
                    self.tiles[tile].append((direction, 0))

        for entity in self.entities.copy():
            entity.update(game_state)
            if game_state.tile_map.get_tile(game_state, entity.position).tile_type == TileType.FINISH:
                self.entities.remove(entity)

        if not game_state.entity_placement_mode:
            return

        for click in game_state.mouse_clicks.copy():
            position = game_state.to_tile_map_space(click.pos)
            if game_state.tile_map.is_on_map(game_state, position, True):
                if game_state.tile_map.get_tile(game_state, position, True).is_walkable:
                    self.spawn_random_entity(position)
                    game_state.mouse_clicks.remove(click)
