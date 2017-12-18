from game_types import GameMode
from helper import Vector, process_clicks, MouseClick
from user_interface.components import TextComponent


class MainMenu:
    def __init__(self):
        self.position = Vector()
        self.components = {
            "editor_button": TextComponent("Editor", Vector(), Vector(300, 50))
        }

    def render(self, game_state):
        for component in self.components:
            self.components[component].render(self.position)

    def update(self, game_state):
        self.position = Vector(game_state.window_size.x / 2 - 150, game_state.window_size.y / 2 + 200)
        process_clicks(game_state, self.mouse_click_handler, False, self.position)

    def mouse_click_handler(self, game_state, click: MouseClick) -> bool:
        for component in self.components:
            if self.components[component].is_clicked(click):
                game_state.mode = GameMode.EDITOR
                return True
        return False
