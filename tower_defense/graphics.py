import os
from typing import Dict, List

import pyglet
from pyglet.gl import *

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
        def load_image(path: str) -> pyglet.image.Texture:
            return pyglet.image.load(os.path.join(base_path, path)).get_texture()

        grass_texture = load_image('grass.jpg')
        sand_texture = load_image('sand.jpg')
        self.tiles = {
            TileType.BUILDING_GROUND: pyglet.graphics.TextureGroup(grass_texture),
            TileType.PATH: pyglet.graphics.TextureGroup(sand_texture)
        }

        boulder_texture = load_image('boulder.png')
        self.entities = {
            EntityType.LARGE_BOULDER: pyglet.graphics.TextureGroup(boulder_texture),
            EntityType.SMALL_BOULDER: pyglet.graphics.TextureGroup(boulder_texture)
        }

        # TODO find bullet texture
        bullet_texture = load_image('ball.png')
        self.bullets = {
            BulletType.STANDARD: pyglet.graphics.TextureGroup(bullet_texture),
            BulletType.DYNAMITE: pyglet.graphics.TextureGroup(bullet_texture)
        }

        tower_texture = load_image('tower.png')
        platform_texture = load_image('platform.png')
        self.buildings = {
            BuildingType.LASER: pyglet.graphics.TextureGroup(tower_texture),
            BuildingType.CATAPULT: pyglet.graphics.TextureGroup(tower_texture),
            BuildingType.DRILL: pyglet.graphics.TextureGroup(platform_texture)
        }

        arrow_texture = load_image('arrow.png')
        ring_texture = load_image('ring.png')
        drill_texture = load_image('drill.png')
        self.other = {
            'arrow': pyglet.graphics.TextureGroup(arrow_texture),
            'ring': pyglet.graphics.TextureGroup(ring_texture),
            'drill': pyglet.graphics.TextureGroup(drill_texture)
        }


class Renderer:
    @staticmethod
    def textured_rectangle(batch: pyglet.graphics.Batch, texture_group: pyglet.graphics.TextureGroup, position: Vector,
                           size: Vector, tex_max: float = 1.0, tex_min: float = 0.0,
                           texture_coords: List[int] = None):
        """
        :param batch:
        :param texture_group:
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
        batch.add(4, pyglet.graphics.GL_QUADS, texture_group, ('v2f/static', vertices), ('t2f/static', texture_coords))

    @staticmethod
    def colored_rectangle(batch: pyglet.graphics.Batch, color: (int, int, int), position: Vector, size: Vector):
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

    @staticmethod
    def rectangle_border(batch: pyglet.graphics.Batch, position: Vector, rect_size: Vector, color=(0, 0, 0),
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
        Renderer.colored_rectangle(batch, color, bottom_left, size)

        # right
        bottom_left = position + Vector(rect_size.x - border_width, 0)
        size = Vector(border_width, rect_size.y - border_width)
        Renderer.colored_rectangle(batch, color, bottom_left, size)

        # top
        bottom_left = position + Vector(border_width, rect_size.y - border_width)
        size = Vector(rect_size.x - border_width, border_width)
        Renderer.colored_rectangle(batch, color, bottom_left, size)

        # left
        bottom_left = position + Vector(0, border_width)
        size = Vector(border_width, rect_size.y - border_width)
        Renderer.colored_rectangle(batch, color, bottom_left, size)


class MovementGroup(pyglet.graphics.Group):
    def __init__(self, angle: float, position: Vector, parent: pyglet.graphics.Group = None):
        super().__init__(parent)
        self.angle = angle
        self.position = position

    def set_state(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(self.position.x, self.position.y, 0)
        glRotatef(self.angle, 0, 0, 1)

    # noinspection PyMethodMayBeStatic
    def unset_state(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
