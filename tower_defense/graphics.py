from typing import Dict

import pygame

from game_types import TileType, EntityType


class Textures:
    def __init__(self):
        self.tiles: Dict[TileType, pygame.Surface] = {
            TileType.GRASS: pygame.image.load('./res/grass.jpg'),
            TileType.SAND: pygame.image.load('./res/sand.jpg')
        }
        self.entities: Dict[EntityType, pygame.Surface] = {
            # EntityType.WARRIOR: pygame.image.load('./res/warrior.')
        }
