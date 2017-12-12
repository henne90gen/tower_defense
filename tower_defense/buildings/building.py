import math
import pyglet

from game_types import BuildingType
from graphics import render_textured_rectangle
from helper import Vector


class Building:
    def __init__(self, position: Vector, size: Vector):
        self.position = position
        self.size = size
        self.building_type = BuildingType.TOWER
        self.initial_cool_down = 10
        self.cool_down = 0

    @property
    def range(self):
        if self.building_type == BuildingType.TOWER:
            return 200
        else:
            return 200

    def render(self, game_state, batch: pyglet.graphics.Batch):
        x = self.position.x * self.size.x + game_state.world_offset.x
        y = self.position.y * self.size.y + game_state.world_offset.y
        if x + self.size.x < 0 or y + self.size.y < 0:
            return
        if x > game_state.window_size.x or y - self.size.y > game_state.window_size.y:
            return

        render_textured_rectangle(batch, game_state.textures.buildings[self.building_type], Vector(x, y), self.size,
                                  tex_max=0.8)

    def update(self, game_state):
        if self.cool_down > 0:
            self.cool_down -= 1

        for entity in game_state.entity_manager.entities:
            world_position = game_state.index_to_world_space(self.position)
            world_position = world_position + self.size / 2
            direction = entity.position - world_position
            distance = direction.length()

            # lead the target in the direction it is going, depending on how far away it is
            direction += entity.velocity * (math.sqrt(distance) * 2)

            if distance < self.range and self.cool_down == 0:
                self.cool_down = self.initial_cool_down
                game_state.building_manager.shoot(world_position, direction)
