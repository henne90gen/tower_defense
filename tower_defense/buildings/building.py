import math

import pyglet

from game_types import BuildingType
from graphics import Renderer, MovementGroup
from helper import Vector, rect_contains_point


class Building:
    def __init__(self, position: Vector, size: Vector, building_type: BuildingType):
        self.position = position
        self.size = size
        self.building_type = building_type
        self.cool_down = 0
        self.mouse_over = False

    @property
    def world_position(self):
        return Vector(self.position.x * self.size.x, self.position.y * self.size.y)

    @property
    def shooting_frequency(self):
        if self.building_type == BuildingType.LASER:
            return 1 / 30
        elif self.building_type == BuildingType.CATAPULT:
            return 1 / 60

    @property
    def range(self):
        if self.building_type == BuildingType.LASER:
            return 200
        elif self.building_type == BuildingType.CATAPULT:
            return 300

    def render(self, game_state, batch: pyglet.graphics.Batch):
        position = game_state.world_to_window_space(self.world_position, self.size)
        if position is None:
            return

        if self.mouse_over:
            size = self.size / self.size.length()
            # exact value is 2 (radius to diameter), but 2.5 'feels' better
            size *= self.range * 2.5
            position -= size / 2
            position += self.size / 2
            Renderer.textured_rectangle(batch, game_state.textures.other['ring'], position, size)

        return position

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


class Laser(Building):
    def render(self, game_state, batch: pyglet.graphics.Batch):
        position = super().render(game_state, batch)
        if position is None:
            return

        Renderer.textured_rectangle(batch, game_state.textures.buildings[self.building_type], position, self.size,
                                    tex_max=0.8)


class Catapult(Building):
    def render(self, game_state, batch: pyglet.graphics.Batch):
        position = super().render(game_state, batch)
        if position is None:
            return

        Renderer.textured_rectangle(batch, game_state.textures.buildings[self.building_type], position, self.size,
                                    tex_max=0.8)


class Drill(Building):
    def __init__(self, position: Vector, size: Vector, building_type: BuildingType):
        super().__init__(position, size, building_type)
        self.angle = 0
        self.drilling_angle = 0
        self.drill_size = Vector(65, 144)

    def update(self, game_state):
        super().update(game_state)

        self.drilling_angle += 1
        if self.drilling_angle > 360:
            self.drilling_angle = 0

    def render(self, game_state, batch: pyglet.graphics.Batch):
        position = super().render(game_state, batch)
        if position is None:
            return

        Renderer.textured_rectangle(batch, game_state.textures.other['platform'], position, self.size)

        texture = game_state.textures.buildings[self.building_type].texture
        position += self.size / 2
        group = MovementGroup(texture, self.angle, position)

        drilling = math.sin(self.drilling_angle) * 10
        offset = Vector(self.drill_size.x / -4, self.drill_size.y / -1.5 + drilling)
        Renderer.textured_rectangle(batch, group, offset, self.drill_size)
