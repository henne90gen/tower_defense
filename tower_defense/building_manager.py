from typing import List

import pyglet

from game_types import BuildingType
from graphics import render_textured_rectangle
from helper import Vector, process_clicks


class Building:
    def __init__(self, position: Vector, size: Vector):
        self.position = position
        self.size = size
        self.building_type = BuildingType.TOWER

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
        pass


class BuildingManager:
    def __init__(self):
        self.buildings: List[Building] = []

    def render(self, game_state):
        batch = pyglet.graphics.Batch()
        for building in self.buildings:
            building.render(game_state, batch)
        batch.draw()

    def update(self, game_state):
        for building in self.buildings:
            building.update(game_state)

        process_clicks(game_state, self.mouse_click_handler)

    def spawn_building(self, game_state, position: Vector):
        building = Building(position, game_state.tile_map.tile_size)
        self.buildings.append(building)

    def mouse_click_handler(self, game_state, click):
        if game_state.tile_map.is_on_map(game_state, click.position, False):
            position = game_state.tile_map.get_tile_index(game_state, click.position, False)
            self.spawn_building(game_state, Vector(position[0], position[1]))
            return True
        return False
