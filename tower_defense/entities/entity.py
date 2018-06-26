import pyglet

from ..game_types import EntityType
from ..graphics import Renderer
from ..helper import Vector


class Entity:
    def __init__(self, position: Vector, size: Vector, entity_type: EntityType):
        self.entity_type = entity_type
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

    def get_movement_target(self, game_state):
        tile = game_state.tile_map.tiles[self.next_tile_index]
        half_tile_size = tile.size / 2
        return tile.world_position + half_tile_size

    def calculate_movement(self, game_state):
        target = self.get_movement_target(game_state)

        desired_velocity = target - self.position
        desired_speed = desired_velocity.length()
        desired_velocity /= desired_speed
        desired_velocity *= self.max_speed
        steer = desired_velocity - self.velocity

        self.acceleration += steer
        self.velocity += self.acceleration
        self.position += self.velocity
        self.acceleration = Vector()

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
        position = game_state.world_to_window_space(self.position, self.size, True)
        if position is None:
            return

        Renderer.textured_rectangle(batch, game_state.textures.entities[self.entity_type], position, self.size,
                                    tex_max=0.775)

    def take_damage(self, damage):
        self.health -= damage


class SmallBoulder(Entity):
    def __init__(self, position: Vector, size: Vector, path_side: int):
        super().__init__(position, size, EntityType.SMALL_BOULDER)
        self.path_side = path_side

    def get_movement_target(self, game_state):
        tile = game_state.tile_map.tiles[self.next_tile_index]
        half_tile_size = tile.size / 2
        center = tile.world_position + half_tile_size
        quarter_tile_size = half_tile_size / 2
        return center + quarter_tile_size * self.path_side
