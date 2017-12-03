from typing import List

import pygame

from game_types import EntityType
from graphics import Textures
from helper import MouseClick, KeyPresses


class Entity:
    def __init__(self, position: (int, int)):
        self.position = position
        self.entity_type = EntityType.WARRIOR

    def render(self, screen: pygame.Surface, textures: Textures):
        # textures.entities[self.entity_type]
        pass


class EntityManager:
    def __init__(self):
        self.entities: List[Entity] = []

    def render(self, screen: pygame.Surface, textures: Textures):
        for entity in self.entities:
            entity.render(screen, textures)

    def update(self, game_state, key_presses: KeyPresses, mouse_clicks: List[MouseClick]):
        pass
