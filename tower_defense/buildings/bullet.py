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
