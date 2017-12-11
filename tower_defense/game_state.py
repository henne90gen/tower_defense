from typing import List

import pyglet

from building_manager import BuildingManager
from entity_manager import EntityManager
from game_types import GameMode
from graphics import Textures
from helper import KeyPresses, MouseClick, Vector
from tile_map import TileMap
from user_interface import HUD


class GameState:
    def __init__(self):
        self.mode = GameMode.NORMAL

        self.window = pyglet.window.Window(width=1280, height=720, resizable=True)
        self.window.set_caption("Tower Defense")

        self.hud: HUD = HUD()

        self.textures: Textures = Textures()

        self.entity_manager: EntityManager = EntityManager()

        self.building_manager: BuildingManager = BuildingManager()

        self.tile_map: TileMap = TileMap()
        self.tile_map.load(self, "./res/maps/basic.map")

        self.key_presses: KeyPresses = KeyPresses()
        self.mouse_clicks: List[MouseClick] = []
        self.mouse_position: (int, int) = (0, 0)

        self.world_offset: Vector = Vector(self.tile_map.border_width * 2,
                                           self.tile_map.border_width * 2)

    @property
    def editor_mode(self) -> bool:
        return self.mode == GameMode.NORMAL

    @property
    def test_mode(self) -> bool:
        return self.mode == GameMode.TEST

    @property
    def building_mode(self) -> bool:
        return self.mode == GameMode.BUILDING

    @property
    def window_size(self) -> Vector:
        return Vector(*self.window.get_size())

    def to_tile_map_space(self, pos: Vector) -> Vector:
        return pos - self.world_offset

    def clean_up(self):
        self.mouse_clicks = []
        self.key_presses.text = ""
        self.key_presses.back_space = False

    def update(self):
        scroll_speed = 5
        if self.key_presses.up:
            self.world_offset.y -= scroll_speed
        if self.key_presses.down:
            self.world_offset.y += scroll_speed
        if self.key_presses.left:
            self.world_offset.x += scroll_speed
        if self.key_presses.right:
            self.world_offset.x -= scroll_speed

        self.world_offset = self.constrain_to_bounds(self.window_size, self.world_offset,
                                                     self.tile_map.tile_map_width,
                                                     self.tile_map.tile_map_height)

    @staticmethod
    def constrain_to_bounds(window_size: Vector, pos: Vector, width: int, height: int) -> Vector:
        screen_width_half = window_size.x / 2
        screen_height_half = window_size.y / 2
        if pos.x > screen_width_half:
            pos.x = screen_width_half
        elif pos.x < -(width - screen_width_half):
            pos.x = -(width - screen_width_half)
        if pos.y > screen_height_half:
            pos.y = screen_height_half
        elif pos.y < -(height - screen_height_half):
            pos.y = -(height - screen_height_half)
        return pos
