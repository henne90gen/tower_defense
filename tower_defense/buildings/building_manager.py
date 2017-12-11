from typing import List, Dict

import pyglet

from buildings.building import Building
from buildings.bullet import Bullet
from helper import Vector, process_clicks


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
