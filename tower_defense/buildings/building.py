import math
import pyglet

from game_types import BuildingType
from graphics import render_textured_rectangle
from helper import Vector


class Building:
    def __init__(self, position: Vector, size: Vector, building_type: BuildingType):
        self.position = position
        self.size = size
        self.building_type = building_type
        self.initial_cool_down = 10
        self.cool_down = 0

    @property
    def world_position(self):
        return Vector(self.position.x * self.size.x, self.position.y * self.size.y)

    @property
    def range(self):
        # TODO make this dependent on the building type
        return 200

    def render(self, game_state, batch: pyglet.graphics.Batch):
        position = game_state.world_to_window_space(self.world_position, self.size)
        if position is None:
            return

        render_textured_rectangle(batch, game_state.textures.buildings[self.building_type], position, self.size,
                                  tex_max=0.8)

    def update(self, game_state):
        if self.cool_down > 0:
            self.cool_down -= 1
            return

        for entity in game_state.entity_manager.entities:
            world_position = game_state.index_to_world_space(self.position)
            world_position = world_position + self.size / 2
            direction = entity.position - world_position
            distance = direction.length()

            # lead the target in the direction it is going, depending on how far away it is
            direction += entity.velocity * (math.sqrt(distance) * 2)

            if distance < self.range:
                self.cool_down = self.initial_cool_down
                game_state.building_manager.shoot(world_position, direction)
