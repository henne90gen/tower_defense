from typing import List

from buildings.building_manager import BuildingManager
from entities.entity_manager import EntityManager
from game_types import GameMode
from graphics import Textures
from helper import KeyPresses, MouseClick, Vector, constrain_rect_to_bounds
from tiles.tile_map import TileMap
from user_interface.user_interface import HUD


class GameState:
    def __init__(self):
        self.mode = GameMode.BUILDING
        self.window_size = Vector()
        self.key_presses: KeyPresses = KeyPresses()
        self.mouse_clicks: List[MouseClick] = []
        self.mouse_position: (int, int) = (0, 0)

        self.hud: HUD = HUD()
        self.textures: Textures = Textures()
        self.tile_map: TileMap = TileMap()
        self.entity_manager: EntityManager = EntityManager()
        self.building_manager: BuildingManager = BuildingManager()

        self.player_health = 100

        self.world_offset: Vector = Vector(self.tile_map.border_width * 2,
                                           self.tile_map.border_width * 2)

    def init(self, base_path: str = './res'):
        self.tile_map.load(self, base_path + "/maps/basic.map")
        self.textures.load(base_path)

    @property
    def editor_mode(self) -> bool:
        return self.mode == GameMode.NORMAL

    @property
    def test_mode(self) -> bool:
        return self.mode == GameMode.TEST

    @property
    def building_mode(self) -> bool:
        return self.mode == GameMode.BUILDING

    def world_to_window_space(self, position: Vector, size: Vector, center_position: bool = False) -> Vector:
        if center_position:
            position = Vector(position.x - size.x / 2, position.y - size.y / 2)

        position += self.world_offset
        if position.x + size.x < 0 or position.y + size.y < 0:
            return None
        if position.x > self.window_size.x or position.y - size.y > self.window_size.y:
            return None

        return position

    def world_to_index_space(self, position: Vector) -> (int, int):
        return int(position.x / self.tile_map.tile_size.x), int(position.y / self.tile_map.tile_size.y)

    def index_to_world_space(self, index: (int, int)) -> Vector:
        # TODO change indexes to Vector objects
        if type(index) == tuple:
            x = index[0]
            y = index[1]
        else:
            x = index.x
            y = index.y
        return Vector(x * self.tile_map.tile_size.x, y * self.tile_map.tile_size.y)

    def window_to_world_space(self, position: Vector) -> Vector:
        return position - self.world_offset

    def clean_up(self):
        self.mouse_clicks = []
        self.key_presses.text = ""
        self.key_presses.back_space = False

    def update(self, window_size: Vector):
        self.window_size = window_size

        scroll_speed = 5
        if self.key_presses.up:
            self.world_offset.y -= scroll_speed
        if self.key_presses.down:
            self.world_offset.y += scroll_speed
        if self.key_presses.left:
            self.world_offset.x += scroll_speed
        if self.key_presses.right:
            self.world_offset.x -= scroll_speed

        rect_size = Vector(self.tile_map.tile_map_width, self.tile_map.tile_map_height)
        self.world_offset = constrain_rect_to_bounds(self.window_size, self.world_offset, rect_size)
