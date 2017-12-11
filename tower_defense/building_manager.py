from typing import List, Dict

import pyglet

from game_types import BuildingType
from graphics import render_textured_rectangle
from helper import Vector, process_clicks


class Building:
    def __init__(self, position: Vector, size: Vector):
        self.position = position
        self.size = size
        self.building_type = BuildingType.TOWER

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
        for entity in game_state.entity_manager.entities:
            world_position = game_state.tile_map.get_tile_position(self.position)
            world_position = world_position + self.size / 2
            distance = (entity.position - world_position).length()
            # if distance < self.range:
            #     game_state.building_manager.shoot(world_position)


class Bullet:
    def __init__(self, position, velocity, size):
        self.position = position
        self.size = size
        self.velocity = velocity

    def render(self, batch, game_state):
        x = self.position.x + game_state.world_offset.x
        y = self.position.y + game_state.world_offset.y
        if x + self.size.x < 0 or y + self.size.y < 0:
            return
        if x > game_state.window_size.x or y - self.size.y > game_state.window_size.y:
            return

        render_textured_rectangle(batch, game_state.textures.buildings[self.building_type], Vector(x, y), self.size,
                                  tex_max=0.8)

    def update(self, game_state):
        pass


class BuildingManager:
    def __init__(self):
        self.buildings: Dict[(int, int), Building] = {}
        self.bullets: List[Bullet] = []

    def render(self, game_state):
        batch = pyglet.graphics.Batch()
        for index in self.buildings:
            self.buildings[index].render(game_state, batch)
        batch.draw()

    def update(self, game_state):
        for index in self.buildings:
            self.buildings[index].update(game_state)

        if game_state.building_mode:
            process_clicks(game_state, self.mouse_click_handler)

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
