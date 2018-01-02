import math

import pyglet

from game_types import BuildingType, TileType
from graphics import Renderer, MovementGroup
from helper import Vector, rect_contains_point


class Building:
    def __init__(self, position: Vector, size: Vector, building_type: BuildingType):
        self.position = position
        self.size = size
        self.building_type = building_type
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
            return 350
        elif self.building_type == BuildingType.CATAPULT:
            return 300
        elif self.building_type == BuildingType.DRILL:
            return 150

        print("Missing range for", self.building_type)
        return -1

    @property
    def cost(self):
        if self.building_type == BuildingType.LASER:
            return 20
        elif self.building_type == BuildingType.CATAPULT:
            return 50
        elif self.building_type == BuildingType.DRILL:
            return 30

        print("Missing cost for", self.building_type)
        return -1

    def render(self, game_state, batch: pyglet.graphics.Batch, tex_max: float = 0.8,
               foreground: pyglet.graphics.Group = None, background: pyglet.graphics.Group = None):
        position = game_state.world_to_window_space(self.world_position, self.size)
        if position is None:
            return

        if self.mouse_over:
            size = self.size / self.size.length()
            # exact value is 2 (radius to diameter), but 2.5 'feels' better
            size *= self.range * 2.5
            ring_position = position - size / 2
            ring_position += self.size / 2
            Renderer.textured_rectangle(batch, game_state.textures.other['ring'], ring_position, size)

        return position

    def update(self, game_state):
        position = game_state.world_to_window_space(self.world_position, self.size)
        if position:  # building is actually on screen
            position += Vector(0, self.size.y)
            self.mouse_over = rect_contains_point(game_state.mouse_position, position, self.size)


class Laser(Building):
    def __init__(self, position: Vector, size: Vector):
        super().__init__(position, size, BuildingType.LASER)
        self.target = None

    def render(self, game_state, batch: pyglet.graphics.Batch, tex_max=0.5, foreground: pyglet.graphics.Group = None,
               background: pyglet.graphics.Group = None):
        position = super().render(game_state, batch)
        if position is None:
            return

        texture = game_state.textures.buildings[self.building_type].texture
        group = pyglet.graphics.TextureGroup(texture, parent=foreground)
        Renderer.textured_rectangle(batch, group, position, self.size,
                                    tex_max=0.5)

        if self.target is None:
            return

        size = Vector(self.target[1], 10)
        angle = self.target[2].angle() / math.pi * 180
        position += self.size / 2 + Vector(0, 35)
        Renderer.colored_rectangle(batch, (0, 255, 255), position, size, angle, background)

    def update(self, game_state):
        super().update(game_state)

        self.target = None
        for entity in game_state.entity_manager.entities:
            world_position = game_state.index_to_world_space(self.position)
            world_position = world_position + self.size / 2
            direction = entity.position - world_position

            distance = direction.length()
            if distance < self.range:
                self.target = entity.position, distance, direction


class Catapult(Building):
    def __init__(self, position: Vector, size: Vector):
        super().__init__(position, size, BuildingType.CATAPULT)

    def update(self, game_state):
        pass
        # lead the target in the direction it is going, depending on how far away it is
        # direction += entity.velocity * (math.sqrt(distance) * 2)


class Drill(Building):
    def __init__(self, position: Vector, size: Vector):
        super().__init__(position, size, BuildingType.DRILL)
        self.rotation_angle = 0
        self.rotation_speed = 2

        self.animation_angle = 0
        self.animation_speed = 0
        self.max_animation_speed = 50

        self.drill_size = Vector(65, 144)

        self.sight_range = 150

    def update(self, game_state):
        super().update(game_state)

        self.animation_angle += self.animation_speed
        if self.animation_angle > 360:
            self.animation_angle = 0

        something_in_sight = self.check_for_entities(game_state)

        if not something_in_sight:
            if self.animation_speed > 0:
                self.animation_speed -= 5

            self.rotate_towards(self.closest_tile_angle(game_state))

    def closest_tile_angle(self, game_state) -> float:
        def test_tile(x, y):
            x += self.position.x
            y += self.position.y
            if (x, y) not in game_state.tile_map.tiles:
                return False
            return game_state.tile_map.tiles[(x, y)].tile_type != TileType.BUILDING_GROUND

        if test_tile(-1, 0):
            return -90
        elif test_tile(1, 0):
            return 90
        elif test_tile(0, -1):
            return 0
        elif test_tile(0, 1):
            return 180
        return 0

    def check_for_entities(self, game_state):
        something_in_sight = False
        for entity in game_state.entity_manager.entities:
            world_position = game_state.index_to_world_space(self.position)
            world_position = world_position + self.size / 2
            direction = entity.position - world_position

            distance = direction.length()
            if distance < self.sight_range:
                angle = direction.angle() * 180 / math.pi + 90
                self.rotate_towards(angle)

                if self.animation_speed < self.max_animation_speed:
                    self.animation_speed += 5
                something_in_sight = True

            if distance < self.range:
                entity.take_damage(1)
                break

        return something_in_sight

    def rotate_towards(self, angle):
        angle -= self.rotation_angle
        if angle != 0:
            self.rotation_angle += angle / abs(angle) * self.rotation_speed

    def render(self, game_state, batch: pyglet.graphics.Batch, tex_max: float = 1.0,
               foreground: pyglet.graphics.Group = None, background: pyglet.graphics.Group = None):
        position = super().render(game_state, batch)
        if position is None:
            return

        texture = game_state.textures.buildings[self.building_type].texture
        group = pyglet.graphics.TextureGroup(texture, parent=background)
        Renderer.textured_rectangle(batch, group, position, self.size,
                                    tex_max=1.0)

        texture = game_state.textures.other['drill'].texture
        position += self.size / 2
        movement_group = MovementGroup(self.rotation_angle, position, foreground)
        texture_group = pyglet.graphics.TextureGroup(texture, movement_group)

        drilling = math.sin(self.animation_angle * math.pi / 180) * 10
        offset = Vector(self.drill_size.x / -4, self.drill_size.y / -1.5 + drilling)
        Renderer.textured_rectangle(batch, texture_group, offset, self.drill_size)
