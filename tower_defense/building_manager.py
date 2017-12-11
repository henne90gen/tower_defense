from typing import List, Dict, Callable

import math
import pyglet

from game_types import BuildingType, BulletType
from graphics import render_textured_rectangle
from helper import Vector, process_clicks, rect_contains_point


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

    def render(self, game_state, batch):
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
            world_position = game_state.tile_map.get_tile_position(self.position)
            world_position = world_position + self.size / 2
            direction = entity.position - world_position
            distance = direction.length()
            direction += entity.velocity * (math.sqrt(distance) * 2)
            if distance < self.range and self.cool_down == 0:
                self.cool_down = self.initial_cool_down
                game_state.building_manager.shoot(world_position, direction)


class Bullet:
    def __init__(self, position: Vector, size: Vector, velocity: Vector):
        self.position = position
        self.size = size
        self.velocity = velocity
        self.bullet_type = BulletType.STANDARD

    @property
    def damage(self):
        # TODO make this dependent on the bullet type
        return 10

    def render(self, batch, game_state):
        x = self.position.x + game_state.world_offset.x
        y = self.position.y + game_state.world_offset.y
        if x + self.size.x < 0 or y + self.size.y < 0:
            return
        if x > game_state.window_size.x or y - self.size.y > game_state.window_size.y:
            return

        render_textured_rectangle(batch, game_state.textures.bullets[self.bullet_type], Vector(x, y), self.size,
                                  tex_max=1.0)

    def update(self, game_state):
        self.position += self.velocity

        for entity in game_state.entity_manager.entities:
            position = Vector(entity.position.x, entity.position.y)
            position.x -= entity.size.x / 2
            position.y += entity.size.y / 2
            if rect_contains_point(self.position, position, entity.size):
                entity.take_damage(self.damage)
                return True

        return not game_state.tile_map.is_on_map(self.position)


class BuildingManager:
    def __init__(self):
        self.bullet_size = Vector(25, 25)
        self.bullet_speed = 5
        self.buildings: Dict[(int, int), Building] = {}
        self.bullets: List[Bullet] = []

    def render(self, game_state):
        batch = pyglet.graphics.Batch()
        for index in self.buildings:
            self.buildings[index].render(game_state, batch)
        batch.draw()

        bullet_batch = pyglet.graphics.Batch()
        for bullet in self.bullets:
            bullet.render(bullet_batch, game_state)
        bullet_batch.draw()

    def update(self, game_state):
        for index in self.buildings:
            self.buildings[index].update(game_state)

        for bullet in self.bullets.copy():
            if bullet.update(game_state):
                print("Removing bullet")
                self.bullets.remove(bullet)

        if game_state.building_mode:
            process_clicks(game_state, self.mouse_click_handler)

    def shoot(self, world_position: Vector, direction: Vector):
        bullet = Bullet(world_position, self.bullet_size, direction / direction.length() * self.bullet_speed)
        self.bullets.append(bullet)

    def spawn_building(self, game_state, tile_index: (int, int)):
        position = Vector(point=tile_index)
        building = Building(position, game_state.tile_map.tile_size)
        self.buildings[tile_index] = building

    def mouse_click_handler(self, game_state, click):
        if game_state.tile_map.is_on_map(click.position):
            tile_index = game_state.tile_map.get_tile_index(click.position)
            if tile_index not in self.buildings:
                self.spawn_building(game_state, tile_index)
            else:
                del self.buildings[tile_index]
            return True
        return False
