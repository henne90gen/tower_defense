from typing import List

import pygame

from game_types import EntityType


class Entity:
    def __init__(self, position: (int, int)):
        self.position = position
        self.entity_type = EntityType.WARRIOR

    def update(self, game_state):
        tile = game_state.tile_map.get_tile(game_state, self.position)
        x, y = self.position
        x += tile.direction[0]
        y += tile.direction[1]
        self.position = x, y

    def render(self, game_state, screen: pygame.Surface):
        texture = game_state.textures.entities[self.entity_type]
        x, y = self.position
        x -= texture.get_width() / 2 - game_state.world_offset_x
        y -= texture.get_height() / 2 - game_state.world_offset_y
        screen.blit(texture, (x, y))


class EntityManager:
    def __init__(self):
        self.entities: List[Entity] = []

    def render(self, game_state, screen: pygame.Surface):
        for entity in self.entities:
            entity.render(game_state, screen)

    def spawn_random_entity(self, position: (int, int)):
        entity = Entity(position)
        self.entities.append(entity)

    def update(self, game_state):

        for entity in self.entities:
            entity.update(game_state)

        if not game_state.entity_placement_mode:
            return

        for click in game_state.mouse_clicks.copy():
            position = game_state.to_world_space(click.pos)
            if game_state.tile_map.is_on_map(game_state, position, True):
                if game_state.tile_map.get_tile(game_state, position, True).is_walkable:
                    self.spawn_random_entity(position)
                    game_state.mouse_clicks.remove(click)
