import pyglet

from game_types import EntityType
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
        self.health = 100
        self.player_damage = 1

    def update(self, game_state):
        if not game_state.tile_map.is_on_map(self.position):
            return

        tile_index = game_state.world_to_index_space(self.position)
        tile = game_state.tile_map.tiles[tile_index]

        if len(tile.directions) == 0:
            return
        if self.next_tile_index is None:
            self.next_tile_index = game_state.world_to_index_space(self.position)

        self.update_next_tile_index(game_state)

        self.calculate_movement(game_state)

    def calculate_movement(self, game_state):
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

    def update_next_tile_index(self, game_state):
        if game_state.world_to_index_space(self.position) == self.next_tile_index:
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

    def render(self, game_state, batch: pyglet.graphics.Batch):
        position = Vector(self.position.x - self.size.x / 2, self.position.y)
        position = game_state.world_to_window_space(position, self.size)
        if position is None:
            return

        x, y = position.x, position.y
        y -= self.size.y / 2

        render_textured_rectangle(batch, game_state.textures.entities[self.entity_type], Vector(x, y), self.size)

    def take_damage(self, damage):
        self.health -= damage
