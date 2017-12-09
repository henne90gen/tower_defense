from typing import Dict, List

import os
import pyglet

from game_types import TileType, EntityType, BuildingType
from helper import Vector


class Textures:
    def __init__(self, base_path: str = "./res"):
        grass_texture = pyglet.image.load(os.path.join(base_path, 'grass.jpg')).get_texture()
        sand_texture = pyglet.image.load(os.path.join(base_path, 'sand.jpg')).get_texture()
        self.tiles: Dict[TileType, pyglet.graphics.TextureGroup] = {
            TileType.BUILDING_GROUND: pyglet.graphics.TextureGroup(grass_texture),
            TileType.PATH: pyglet.graphics.TextureGroup(sand_texture)
        }

        ball_texture = pyglet.image.load(os.path.join(base_path, 'ball.png')).get_texture()
        self.entities: Dict[EntityType, pyglet.graphics.TextureGroup] = {
            EntityType.WARRIOR: pyglet.graphics.TextureGroup(ball_texture)
        }

        tower_texture = pyglet.image.load(os.path.join(base_path, 'tower.png')).get_texture()
        self.buildings: Dict[BuildingType, pyglet.graphics.TextureGroup] = {
            BuildingType.TOWER: pyglet.graphics.TextureGroup(tower_texture)
        }

        arrow_texture = pyglet.image.load(os.path.join(base_path, 'arrow.png')).get_texture()
        self.other: Dict[str, pyglet.graphics.TextureGroup] = {
            'arrow': pyglet.graphics.TextureGroup(arrow_texture)
        }


def render_textured_rectangle(batch, texture, position: Vector, size: Vector, tex_max: float = 1.0,
                              tex_min: float = 0.0, texture_coords: List[int] = None):
    """
    :param batch:
    :param texture:
    :param position: bottom left of rectangle
    :param size:
    :param tex_max:
    :param tex_min:
    :param texture_coords:
    :return:
    """
    top_left = Vector(position.x, position.y + size.y)
    bottom_right = Vector(top_left.x + size.x, top_left.y - size.y)
    vertices = [bottom_right.x, bottom_right.y,
                bottom_right.x, top_left.y,
                top_left.x, top_left.y,
                top_left.x, bottom_right.y]
    if texture_coords is None:
        texture_coords = [tex_max, tex_min,
                          tex_max, tex_max,
                          tex_min, tex_max,
                          tex_min, tex_min]
    batch.add(4, pyglet.graphics.GL_QUADS, texture, ('v2f/static', vertices), ('t2f/static', texture_coords))


def render_colored_rectangle(batch, color, position: Vector, size: Vector):
    """
    :param batch:
    :param color:
    :param position: bottom left of rectangle
    :param size:
    :return:
    """
    top_left = Vector(position.x, position.y + size.y)
    bottom_right = Vector(top_left.x + size.x, top_left.y - size.y)
    vertices = [bottom_right.x, bottom_right.y,
                bottom_right.x, top_left.y,
                top_left.x, top_left.y,
                top_left.x, bottom_right.y]
    batch.add(4, pyglet.graphics.GL_QUADS, None, ('v2f/static', vertices),
              ('c3B/static', (*color, *color, *color, *color)))
