from typing import List

import pygame

from entity_manager import EntityManager
from game_types import GameMode
from graphics import Textures
from helper import KeyPresses, MouseClick
from tile_map import TileMap
from user_interface import HUD


class GameState:
    def __init__(self):
        self.mode = GameMode.EDITOR

        self.tile_map: TileMap = TileMap()
        self.tile_map.load("./res/maps/basic.map")

        self.hud: HUD = HUD()

        self.textures: Textures = Textures()

        self.entity_manager: EntityManager = EntityManager()

        self.key_presses: KeyPresses = KeyPresses()
        self.mouse_clicks: List[MouseClick] = []
        self.mouse_position: (int, int) = (0, 0)

        self.world_offset_x = self.world_offset_y = self.tile_map.border_width * 2

    @property
    def editor_mode(self):
        return self.mode == GameMode.EDITOR

    @property
    def entity_placement_mode(self):
        return self.mode == GameMode.ENTITY_PLACEMENT

    def to_world_space(self, pos: (int, int)) -> (int, int):
        x, y = pos
        x -= self.world_offset_x
        y -= self.world_offset_y
        return x, y

    def update(self, screen: pygame.Surface):
        scroll_speed = 5
        if self.key_presses.up:
            self.world_offset_y += scroll_speed
        if self.key_presses.down:
            self.world_offset_y -= scroll_speed
        if self.key_presses.left:
            self.world_offset_x += scroll_speed
        if self.key_presses.right:
            self.world_offset_x -= scroll_speed

        self.world_offset_x, self.world_offset_y = self.constrain_to_bounds(screen, self.world_offset_x,
                                                                            self.world_offset_y,
                                                                            self.tile_map.tile_map_width,
                                                                            self.tile_map.tile_map_height)

    @staticmethod
    def constrain_to_bounds(screen, x, y, width, height) -> (int, int):
        screen_width_half = screen.get_width() / 2
        screen_height_half = screen.get_height() / 2
        if x > screen_width_half:
            x = screen_width_half
        elif x < -(width - screen_width_half):
            x = -(width - screen_width_half)
        if y > screen_height_half:
            y = screen_height_half
        elif y < -(height - screen_height_half):
            y = -(height - screen_height_half)
        return x, y
