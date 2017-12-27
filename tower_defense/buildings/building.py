import math
import pyglet

from game_types import BuildingType
from graphics import render_textured_rectangle
from helper import Vector, rect_contains_point


class Building:
    def __init__(self, position: Vector, size: Vector, building_type: BuildingType):
        self.position = position
        self.size = size
        self.building_type = building_type
        # self.initial_cool_down = 10
        self.cool_down = 0
        self.mouse_over = False

    @property
    def world_position(self):
        return Vector(self.position.x * self.size.x, self.position.y * self.size.y)

    @property
    def shooting_frequency(self):
        if self.building_type == BuildingType.Archer:
            return 1 / 30
        elif self.building_type == BuildingType.Cannon:
            return 1 / 60

    @property
    def range(self):
        if self.building_type == BuildingType.Archer:
            return 200
        elif self.building_type == BuildingType.Cannon:
            return 300

    def render(self, game_state, batch: pyglet.graphics.Batch):
        position = game_state.world_to_window_space(self.world_position, self.size)
        if position is None:
            return

        render_textured_rectangle(batch, game_state.textures.buildings[self.building_type], position, self.size,
                                  tex_max=0.8)
        if self.mouse_over:
            size = self.size / self.size.length()
            # exact value is 2 (radius to diameter), but 2.5 'feels' better
            size *= self.range * 2.5
            position -= size / 2
            position += self.size / 2
            render_textured_rectangle(batch, game_state.textures.other['ring'], position, size)

    def update(self, game_state):
        position = game_state.world_to_window_space(self.world_position, self.size)
        if position:  # building is actually on screen
            position += Vector(0, self.size.y)
            self.mouse_over = rect_contains_point(game_state.mouse_position, position, self.size)

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
                self.cool_down = 1 / self.shooting_frequency
                game_state.building_manager.shoot(world_position, direction)
