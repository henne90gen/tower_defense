from typing import List

from ..game_types import GameMode
from ..helper import Vector, process_clicks, MouseClick, maps_list, get_maps_path
from .components import Button
from .dialogs import NewMapDialog


class MainMenu:
    def __init__(self):
        self.position = Vector()
        button_size = Vector(300, 50)

        self.components = {
            "game_button": Button("Play", Vector(), button_size),
            "editor_button": Button("Editor", Vector(0, -50), button_size),
            "exit_button": Button("Exit", Vector(0, -100), button_size)
        }

        self.handlers = {
            "game_button": self.game_func,
            "editor_button": self.editor_func,
            "exit_button": self.exit_func
        }

    def render(self):
        for component in self.components:
            self.components[component].render(self.position)

    def update(self, game_state):
        self.position = Vector(game_state.window_size.x / 2 - 150, game_state.window_size.y / 2 + 200)
        process_clicks(game_state, self.mouse_click_handler, False, self.position)

    @staticmethod
    def game_func(game_state):
        game_state.mode = GameMode.MAP_CHOICE_GAME

    @staticmethod
    def editor_func(game_state):
        game_state.mode = GameMode.MAP_CHOICE_EDITOR

    @staticmethod
    def exit_func(game_state):
        exit(0)

    def mouse_click_handler(self, game_state, click: MouseClick) -> bool:
        for component in self.components:
            if self.components[component].is_clicked(click):
                if component in self.handlers:
                    self.handlers[component](game_state)
                return True
        return False


class MapMenu:
    def __init__(self, map_path: str = None) -> None:
        self.position = Vector()
        self.map_path = map_path
        if self.map_path is None:
            self.map_path = get_maps_path()

        self.button_size = Vector(300, 50)
        self.back_button = Button("Back", Vector(), self.button_size)
        self.new_button = Button("New", Vector(), self.button_size)
        self.new_dialog = NewMapDialog()

        self.maps: List[Button] = []

    @staticmethod
    def back_func(game_state):
        game_state.mode = GameMode.MAIN_MENU

    def new_func(self, game_state):
        self.new_dialog.open(game_state)

    @staticmethod
    def load_func(game_state, path):
        game_state.tile_map.load(game_state, "./res/maps/" + path)
        if game_state.mode == GameMode.MAP_CHOICE_GAME:
            game_state.mode = GameMode.GAME
        elif game_state.mode == GameMode.MAP_CHOICE_EDITOR:
            game_state.mode = GameMode.EDITOR

    def update(self, game_state):
        self.position = Vector(game_state.window_size.x / 2 - 150, game_state.window_size.y / 2 + 200)

        if game_state.mode == GameMode.MAP_CHOICE_EDITOR and self.new_dialog.visible:
            self.new_dialog.update(game_state)
            return

        if len(self.maps) == 0:
            self.refresh_maps(self.map_path)

        offset = 0
        if game_state.mode == GameMode.MAP_CHOICE_EDITOR:
            self.new_button.position = Vector(y=-self.button_size.y * len(self.maps))
            offset = 1

        self.back_button.position = Vector(y=-self.button_size.y * (len(self.maps) + offset))

        process_clicks(game_state, self.mouse_click_handler, False, self.position)

    def mouse_click_handler(self, game_state, click: MouseClick) -> bool:
        if self.back_button.is_clicked(click):
            self.back_func(game_state)
            return True

        if game_state.mode == GameMode.MAP_CHOICE_EDITOR and self.new_button.is_clicked(click):
            self.new_func(game_state)
            return True

        for m in self.maps:
            if m.is_clicked(click):
                self.load_func(game_state, m.text)
                return True

        return False

    def refresh_maps(self, maps_path: str):
        maps = maps_list(maps_path)
        self.maps = []

        for index, m in enumerate(maps):
            self.maps.append(Button(m, Vector(y=-self.button_size.y * index), self.button_size))

    def render(self, game_state):
        if game_state.mode == GameMode.MAP_CHOICE_EDITOR:
            self.new_dialog.position = Vector(10, self.position.y)
            self.new_dialog.render()
            self.new_button.render(self.position)

        self.back_button.render(self.position)

        for m in self.maps:
            m.render(self.position)
