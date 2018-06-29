from ..game_types import GameMode
from ..helper import Vector, process_clicks, MouseClick
from .components import Button, Label
from .dialogs import Dialog, NewMapDialog, LoadMapDialog, BuildingDialog


class EditorUI:
    def __init__(self):
        button_height = 50
        size = Vector(180, button_height)
        self.components = {
            'menu_button': Button("Menu", Vector(0, 0), size),
            'new_button': Button("New", Vector(0, -1 * button_height), size, visible=False),
            'save_button': Button("Save", Vector(0, -2 * button_height), size, visible=False),
            'load_button': Button("Load", Vector(0, -3 * button_height), size, visible=False),
            'back_button': Button("Back", Vector(0, -4 * button_height), size, visible=False),
            'entities_toggle': Button("", Vector(size.x, 0), size + Vector(20, 0)),
        }
        self.handlers = {
            'menu_button': self.menu_func,
            'save_button': self.save_func,
            'new_button': self.new_func,
            'load_button': self.load_func,
            'back_button': self.back_func,
            'entities_toggle': self.entities_func,
        }
        self.new_dialog: Dialog = NewMapDialog()
        self.load_dialog: Dialog = LoadMapDialog()
        self.offset = Vector(0, 0)

    def menu_func(self, _):
        self.toggle_map_menu()

    def save_func(self, game_state):
        game_state.tile_map.save()
        self.toggle_map_menu()

    def new_func(self, game_state):
        self.toggle_map_menu()
        self.new_dialog.open(game_state)

    def load_func(self, game_state):
        self.toggle_map_menu()
        self.load_dialog.open(game_state)

    @staticmethod
    def back_func(game_state):
        game_state.mode = GameMode.MAIN_MENU

    @staticmethod
    def entities_func(game_state):
        game_state.entity_manager.should_spawn = not game_state.entity_manager.should_spawn
        game_state.entity_manager.reset()

    def update(self, game_state):
        self.offset.y = game_state.window_size.y

        if self.new_dialog.visible:
            self.new_dialog.update(game_state)
        elif self.load_dialog.visible:
            self.load_dialog.update(game_state)
        else:
            text = "Entities" if game_state.entity_manager.should_spawn else "No Entities"
            self.components['entities_toggle'].update(text=text)
            process_clicks(game_state, self.mouse_click_handler, False, offset=self.offset)

    def mouse_click_handler(self, game_state, click):
        for component in self.handlers:
            if self.components[component].is_clicked(click):
                self.handlers[component](game_state)
                return True
        return False

    def toggle_map_menu(self):
        self.components['new_button'].toggle_visibility()
        self.components['save_button'].toggle_visibility()
        self.components['load_button'].toggle_visibility()
        self.components['back_button'].toggle_visibility()

    def render(self):
        for component in self.components:
            self.components[component].render(self.offset)

        self.new_dialog.render()
        self.load_dialog.render()


class GameUI:
    def __init__(self):
        self.offset = Vector()
        button_height = 50
        size = Vector(180, button_height)
        self.components = {
            'next_wave_button': Button("Next Wave", Vector(), size),
            'current_wave_label': Label("", Vector(size.x, 0), size),
            'health_label': Label("", Vector(size.x * 2, 0), size),
            'gold_label': Label("", Vector(size.x * 3, 0), size),
            'game_over_label': Label("Game Over", Vector(0, -100), Vector(400, 90), font_size=50, visible=False)
        }
        self.handlers = {
            'next_wave_button': self.next_wave_func
        }
        self.building_dialog = BuildingDialog()

    def update(self, game_state):
        self.offset.y = game_state.window_size.y
        self.components['health_label'].update(text=str(game_state.player_health))
        self.components['gold_label'].update(text=str(game_state.building_manager.gold))
        self.components['current_wave_label'].update(text=str(game_state.entity_manager.wave_count))

        self.components['next_wave_button'].update(disabled=game_state.entity_manager.wave_running)

        self.components['game_over_label'].position.x = game_state.window_size.x / 2 - self.components[
            'game_over_label'].size.x / 2
        if game_state.player_health <= 0:
            self.components['game_over_label'].visible = True
        else:
            self.components['game_over_label'].visible = False

        if game_state.tile_map.highlighted_tile and not self.building_dialog.visible:
            self.building_dialog.open(game_state)
        elif self.building_dialog.visible and not game_state.tile_map.highlighted_tile:
            self.building_dialog.close()

        self.building_dialog.update(game_state)

        process_clicks(game_state, self.mouse_click_handler, False, self.offset)

    @staticmethod
    def next_wave_func(game_state):
        game_state.entity_manager.next_wave()

    def mouse_click_handler(self, game_state, click: MouseClick) -> bool:
        for component in self.components:
            if self.components[component].is_clicked(click) and not self.components[component].disabled:
                if component in self.handlers:
                    self.handlers[component](game_state)
                return True
        return False

    def render(self, _):
        for component in self.components:
            self.components[component].render(self.offset)

        self.building_dialog.render()
