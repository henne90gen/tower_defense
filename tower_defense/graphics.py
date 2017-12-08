from typing import Dict, List

import pyglet

from game_types import TileType, EntityType, BuildingType
from helper import Vector


class Textures:
    def __init__(self):
        self.tiles: Dict[TileType, pyglet.graphics.TextureGroup] = {
            TileType.BUILDING_GROUND: pyglet.graphics.TextureGroup(pyglet.image.load('./res/grass.jpg').get_texture()),
            TileType.PATH: pyglet.graphics.TextureGroup(pyglet.image.load('./res/sand.jpg').get_texture())
        }
        self.entities: Dict[EntityType, pyglet.graphics.TextureGroup] = {
            EntityType.WARRIOR: pyglet.graphics.TextureGroup(pyglet.image.load('./res/ball.png').get_texture())
        }
        self.buildings: Dict[BuildingType, pyglet.graphics.TextureGroup] = {
            BuildingType.TOWER: pyglet.graphics.TextureGroup(pyglet.image.load('./res/tower.png').get_texture())
        }
        self.other: Dict[str, pyglet.graphics.TextureGroup] = {
            'arrow': pyglet.graphics.TextureGroup(pyglet.image.load('./res/arrow.png').get_texture())
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
    :param tex_max:
    :param tex_min:
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
