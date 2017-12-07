from typing import Dict

import pyglet

from game_types import TileType, EntityType


class Textures:
    def __init__(self):
        self.tiles: Dict[TileType, pyglet.graphics.TextureGroup] = {
            TileType.BUILDING_GROUND: pyglet.graphics.TextureGroup(pyglet.image.load('./res/grass.jpg').get_texture()),
            TileType.PATH: pyglet.graphics.TextureGroup(pyglet.image.load('./res/sand.jpg').get_texture())
        }
        self.entities: Dict[EntityType, pyglet.graphics.TextureGroup] = {
            EntityType.WARRIOR: pyglet.graphics.TextureGroup(pyglet.image.load('./res/ball.png').get_texture())
        }
        self.other: Dict[str, pyglet.graphics.TextureGroup] = {
            'arrow': pyglet.graphics.TextureGroup(pyglet.image.load('./res/arrow.png').get_texture())
        }
