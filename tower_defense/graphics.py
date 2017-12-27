from typing import Dict, List

import os
import pyglet

from game_types import TileType, EntityType, BuildingType, BulletType
from helper import Vector


class Textures:
    def __init__(self):
        self.tiles: Dict[TileType, pyglet.graphics.TextureGroup] = {}
        self.entities: Dict[EntityType, pyglet.graphics.TextureGroup] = {}
        self.bullets: Dict[BulletType, pyglet.graphics.TextureGroup] = {}
        self.buildings: Dict[BuildingType, pyglet.graphics.TextureGroup] = {}
        self.other: Dict[str, pyglet.graphics.TextureGroup] = {}

    def load(self, base_path: str = "./res"):
        grass_texture = pyglet.image.load(os.path.join(base_path, 'grass.jpg')).get_texture()
        sand_texture = pyglet.image.load(os.path.join(base_path, 'sand.jpg')).get_texture()
        self.tiles = {
            TileType.BUILDING_GROUND: pyglet.graphics.TextureGroup(grass_texture),
            TileType.PATH: pyglet.graphics.TextureGroup(sand_texture)
        }

        ball_texture = pyglet.image.load(os.path.join(base_path, 'ball.png')).get_texture()
        self.entities = {
            EntityType.WARRIOR: pyglet.graphics.TextureGroup(ball_texture)
        }

        # TODO find bullet texture
        self.bullets = {
            BulletType.STANDARD: pyglet.graphics.TextureGroup(ball_texture)
        }

        tower_texture = pyglet.image.load(os.path.join(base_path, 'tower.png')).get_texture()
        self.buildings = {
            BuildingType.Archer: pyglet.graphics.TextureGroup(tower_texture),
            BuildingType.Cannon: pyglet.graphics.TextureGroup(tower_texture)
        }

        arrow_texture = pyglet.image.load(os.path.join(base_path, 'arrow.png')).get_texture()
        ring_texture = pyglet.image.load(os.path.join(base_path, 'ring.png')).get_texture()
        self.other = {
            'arrow': pyglet.graphics.TextureGroup(arrow_texture),
            'ring': pyglet.graphics.TextureGroup(ring_texture)
        }


def render_textured_rectangle(batch: pyglet.graphics.Batch, texture: pyglet.graphics.TextureGroup, position: Vector,
                              size: Vector, tex_max: float = 1.0, tex_min: float = 0.0,
                              texture_coords: List[int] = None):
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


def render_colored_rectangle(batch: pyglet.graphics.Batch, color: (int, int, int), position: Vector, size: Vector):
    """
    :param batch:
    :param color: triple with values ranging from 0 to 255
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


def render_rectangle_border(batch: pyglet.graphics.Batch, position: Vector, rect_size: Vector, color=(0, 0, 0),
                            border_width=3):
    """
    :param batch:
    :param position: bottom left of rectangle
    :param rect_size:
    :param color:
    :param border_width:
    :return:
    """
    # bottom
    bottom_left = position.copy()
    size = Vector(rect_size.x - border_width, border_width)
    render_colored_rectangle(batch, color, bottom_left, size)

    # right
    bottom_left = position + Vector(rect_size.x - border_width, 0)
    size = Vector(border_width, rect_size.y - border_width)
    render_colored_rectangle(batch, color, bottom_left, size)

    # top
    bottom_left = position + Vector(border_width, rect_size.y - border_width)
    size = Vector(rect_size.x - border_width, border_width)
    render_colored_rectangle(batch, color, bottom_left, size)

    # left
    bottom_left = position + Vector(0, border_width)
    size = Vector(border_width, rect_size.y - border_width)
    render_colored_rectangle(batch, color, bottom_left, size)
