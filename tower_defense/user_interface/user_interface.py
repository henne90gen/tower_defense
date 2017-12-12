from game_types import GameMode
from helper import Vector, process_clicks
from user_interface.dialogs import Dialog, NewMapDialog, LoadMapDialog
from user_interface.components import TextComponent


class HUD:
    def __init__(self):
        button_height = 50
        size = Vector(180, button_height)
        self.components = {
            'map_button': TextComponent("Map", Vector(0, 0), size),
            'new_button': TextComponent("New", Vector(0, -1 * button_height), size, visible=False),
            'save_button': TextComponent("Save", Vector(0, -2 * button_height), size, visible=False),
            'load_button': TextComponent("Load", Vector(0, -3 * button_height), size, visible=False),
            'mode_button': TextComponent("Mode", Vector(size.x, 0), size),
        }
        for index, mode in enumerate(GameMode):
            position = Vector(size.x, -(index + 1) * button_height)
            self.components[mode] = TextComponent(str(mode)[9:], position, size, visible=False)

        self.new_dialog: Dialog = NewMapDialog()
        self.load_dialog: Dialog = LoadMapDialog()
        self.offset = Vector(0, 0)

    def update(self, game_state):
        self.offset.y = game_state.window_size.y

        if self.new_dialog.visible:
            self.new_dialog.update(game_state)
        elif self.load_dialog.visible:
            self.load_dialog.update(game_state)
        else:
            def menu():
                self.toggle_map_menu()

            def mode():
                self.toggle_mode_menu()

            def save():
                game_state.tile_map.save()
                self.toggle_map_menu()

            def new():
                self.toggle_map_menu()
                self.new_dialog.open(game_state)

            def load():
                self.toggle_map_menu()
                self.load_dialog.open(game_state)

            handlers = {
                'map_button': menu,
                'save_button': save,
                'new_button': new,
                'load_button': load,
                'mode_button': mode,
            }

            def create_setter(mode):
                def setter():
                    game_state.mode = mode
                    self.toggle_mode_menu()

                return setter

            for mode in GameMode:
                handlers[mode] = create_setter(mode)

            def processor(_game_state, click):
                for component in handlers:
                    if self.components[component].is_clicked(click):
                        handlers[component]()
                        return True
                return False

            process_clicks(game_state, processor, False, offset=self.offset * -1)

    def toggle_map_menu(self):
        self.components['new_button'].toggle_visibility()
        self.components['save_button'].toggle_visibility()
        self.components['load_button'].toggle_visibility()

    def toggle_mode_menu(self):
        for mode in GameMode:
            self.components[mode].toggle_visibility()

    def render(self):
        for component in self.components:
            self.components[component].render(self.offset)

        self.new_dialog.render()
        self.load_dialog.render()