from game_types import GameMode
from helper import Vector, process_clicks, MouseClick
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
            "game_button": lambda _: None,
            "editor_button": self.editor_func,
            "exit_button": self.exit_func
        }

    def render(self, game_state):
        for component in self.components:
            self.components[component].render(self.position)

    def update(self, game_state):
        self.position = Vector(game_state.window_size.x / 2 - 150, game_state.window_size.y / 2 + 200)
        process_clicks(game_state, self.mouse_click_handler, False, self.position)

    def editor_func(self, game_state):
        game_state.mode = GameMode.EDITOR

    def exit_func(self, game_state):
        exit(0)

    def mouse_click_handler(self, game_state, click: MouseClick) -> bool:
        for component in self.components:
            if self.components[component].is_clicked(click):
                if component in self.handlers:
                    self.handlers[component](game_state)
                return True
        return False
