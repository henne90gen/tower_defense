from typing import Dict

import pygame

from game_types import TileType, EntityType


class Textures:
    def __init__(self):
        self.tiles: Dict[TileType, pygame.Surface] = {
            TileType.BUILDING_GROUND: pygame.image.load('./res/grass.jpg'),
            TileType.PATH: pygame.image.load('./res/sand.jpg')
        }
        self.entities: Dict[EntityType, pygame.Surface] = {
            EntityType.WARRIOR: pygame.image.load('./res/ball.png')
        }
        self.other: Dict[str, pygame.Surface] = {
            'arrow': pygame.image.load('./res/arrow.png')
        }
