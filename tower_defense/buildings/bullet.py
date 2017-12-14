import pyglet

from game_types import BulletType
from graphics import render_textured_rectangle
from helper import Vector, rect_contains_point


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

    def render(self, game_state, batch: pyglet.graphics.Batch):
        position = game_state.world_to_window_space(self.position, self.size, True)
        if position is None:
            return

        render_textured_rectangle(batch, game_state.textures.bullets[self.bullet_type], position, self.size,
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
