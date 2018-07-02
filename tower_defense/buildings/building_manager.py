from typing import List, Dict, Tuple

import pyglet

from .building import Building, Laser, Drill, Hammer
from ..entities.bullet import Bullet
from ..game_types import BuildingType
from ..helper import Vector


class BuildingManager:
    def __init__(self):
        self.gold = 500
        self.bullet_size = Vector(25, 25)
        self.bullet_speed = 5
        self.buildings: Dict[(int, int), Building] = {}
        self.bullets: List[Bullet] = []

    def render(self, game_state):
        batch = pyglet.graphics.Batch()
        foreground = pyglet.graphics.OrderedGroup(1)
        background = pyglet.graphics.OrderedGroup(0)

        for key in self.buildings:
            self.buildings[key].render(game_state, batch, foreground=foreground, background=background)
        batch.draw()

        bullet_batch = pyglet.graphics.Batch()
        for bullet in self.bullets:
            bullet.render(game_state, bullet_batch)
        bullet_batch.draw()

    def update(self, game_state):
        # TODO remove this at some point
        if not self.buildings:
            self.spawn_building(game_state, (3, 4), BuildingType.HAMMER)
        #     self.spawn_building(game_state, (6, 2), BuildingType.LASER)

        for index in self.buildings:
            self.buildings[index].update(game_state)

        for bullet in self.bullets.copy():
            if bullet.update(game_state):
                self.bullets.remove(bullet)

    def shoot(self, world_position: Vector, direction: Vector):
        bullet = Bullet(world_position, self.bullet_size, direction / direction.length() * self.bullet_speed)
        self.bullets.append(bullet)

    def spawn_building(self, game_state, tile_index: Tuple[int, int], building_type: BuildingType):
        position = Vector(point=tile_index)

        args = (position, game_state.tile_map.tile_size, BuildingType.HAMMER)
        building: Building = Building(*args)

        if building_type == BuildingType.LASER:
            building = Laser(*args[:-1])
        elif building_type == BuildingType.DRILL:
            building = Drill(*args[:-1])
        elif building_type == BuildingType.HAMMER:
            building = Hammer(*args[:-1])

        if building.cost > self.gold:
            return

        self.gold -= building.cost
        self.buildings[tile_index] = building
