from typing import List

import pyglet

from .buildings import building_manager as bm
from .entities import entity_manager as em
from .tiles import tile_map as tm
from .user_interface import menu as menu
from .user_interface import user_interface as ui
from .game_types import GameMode
from .graphics import Textures
from .helper import KeyPresses, MouseClick, Vector, constrain_rect_to_bounds


class GameState:
    def __init__(self):
        self.mode = GameMode.MAIN_MENU

        self.window_size = Vector()
        self.key_presses: KeyPresses = KeyPresses()
        self.mouse_clicks: List[MouseClick] = []
        self.mouse_position = Vector()

        self.main_menu: menu.MainMenu = menu.MainMenu()
        self.map_menu: menu.MapMenu = menu.MapMenu()

        self.editor_ui: ui.EditorUI = ui.EditorUI()
        self.game_ui: ui.GameUI = ui.GameUI()

        self.textures: Textures = Textures()
        self.tile_map: tm.TileMap = tm.TileMap()
        self.entity_manager: em.EntityManager = em.EntityManager()
        self.building_manager: bm.BuildingManager = bm.BuildingManager()

        self.player_health = 100

        self.world_offset: Vector = Vector(self.tile_map.border_width * 2,
                                           self.tile_map.border_width * 2)

        self.tickers = {
            GameMode.GAME: self.tick_game,
            GameMode.EDITOR: self.tick_editor,
            GameMode.MAIN_MENU: self.tick_main_menu,
            GameMode.MAP_CHOICE_GAME: self.tick_map_menu,
            GameMode.MAP_CHOICE_EDITOR: self.tick_map_menu,
        }

    def init(self, base_path: str = './res'):
        self.tile_map.load(self, base_path + "/maps/basic.map")
        self.textures.load(base_path)

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

    # noinspection PyUnresolvedReferences
    def index_to_world_space(self, index: Vector) -> Vector:
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

        rect_size = Vector(self.tile_map.tile_map_width, self.tile_map.tile_map_height)
        self.world_offset = constrain_rect_to_bounds(self.window_size, self.world_offset, rect_size)

    def tick_editor(self):
        if type(self.entity_manager) != em.EditorEntityManager:
            self.entity_manager = em.EditorEntityManager()
        if type(self.tile_map) != tm.EditorTileMap:
            path = self.tile_map.path
            self.tile_map = tm.EditorTileMap()
            self.tile_map.load(self, path)

        self.update()

        self.editor_ui.update(self)
        self.entity_manager.update(self)
        self.tile_map.update(self)

        self.tile_map.render(self)
        self.entity_manager.render(self)
        self.editor_ui.render()

    def tick_game(self):
        if type(self.entity_manager) != em.GameEntityManager:
            self.entity_manager = em.GameEntityManager()
        if type(self.tile_map) != tm.GameTileMap:
            path = self.tile_map.path
            self.tile_map = tm.GameTileMap()
            self.tile_map.load(self, path)

        self.update()

        self.game_ui.update(self)
        self.entity_manager.update(self)
        self.building_manager.update(self)
        self.tile_map.update(self)

        self.tile_map.render(self)
        self.building_manager.render(self)
        self.entity_manager.render(self)
        self.game_ui.render(self)

    def tick_main_menu(self):
        self.main_menu.update(self)
        self.main_menu.render()

    def tick_map_menu(self):
        self.map_menu.update(self)
        self.map_menu.render(self)

    def tick(self, window: pyglet.window.Window):
        self.window_size = Vector(*window.get_size())

        self.tickers[self.mode]()
