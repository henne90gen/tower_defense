import os
from typing import List

from game_types import GameMode
from helper import Vector, process_clicks, MouseClick, maps_list
from user_interface.components import TextComponent


class MainMenu:
    def __init__(self):
        self.position = Vector()
        button_size = Vector(300, 50)

        self.components = {
            "game_button": TextComponent("Play", Vector(), button_size),
            "editor_button": TextComponent("Editor", Vector(0, -50), button_size),
            "exit_button": TextComponent("Exit", Vector(0, -100), button_size)
        }

        self.handlers = {
            "game_button": self.game_func,
            "editor_button": self.editor_func,
            "exit_button": self.exit_func
        }

    def render(self, game_state):
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
    def __init__(self):
        self.position = Vector()

        self.button_size = Vector(300, 50)
        self.back_button = TextComponent("Back", Vector(), self.button_size)
        self.maps: List[TextComponent] = []

    @staticmethod
    def back_func(game_state):
        game_state.mode = GameMode.MAIN_MENU

    @staticmethod
    def load_func(game_state, path):
        game_state.tile_map.load(game_state, "./res/maps/" + path)
        if game_state.mode == GameMode.MAP_CHOICE_GAME:
            game_state.mode = GameMode.GAME
        elif game_state.mode == GameMode.MAP_CHOICE_EDITOR:
            game_state.mode = GameMode.EDITOR

    def update(self, game_state):
        self.position = Vector(150, game_state.window_size.y - 100)

        if len(self.maps) == 0:
            self.refresh_maps('./res/maps')

        process_clicks(game_state, self.mouse_click_handler, False, self.position)

    def mouse_click_handler(self, game_state, click: MouseClick) -> bool:
        if self.back_button.is_clicked(click):
            self.back_func(game_state)
            return True
        for m in self.maps:
            if m.is_clicked(click):
                self.load_func(game_state, m.text)
                return True
        return False

    def refresh_maps(self, maps_path: str):
        height = 50
        maps = maps_list(maps_path)
        self.maps = []
        for index, m in enumerate(maps):
            self.maps.append(TextComponent(m, Vector(0, -50 - height * index), Vector(300, height)))

    def render(self):
        self.back_button.render(self.position)
        for m in self.maps:
            m.render(self.position)
