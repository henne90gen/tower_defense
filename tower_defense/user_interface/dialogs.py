from typing import List

import os

from helper import Vector, MouseClick
from user_interface.components import TextComponent, Input

MAPS_PATH = './res/maps/'


class Dialog:
    def __init__(self, visible: bool):
        self.position = Vector()
        self.visible = visible

    def open(self, game_state):
        self.visible = True
        self.position.y = game_state.window_size.y - 200

    def render(self):
        pass

    def update(self, game_state):
        game_state.key_presses.up = game_state.key_presses.down = game_state.key_presses.left = game_state.key_presses.right = False


class NewMapDialog(Dialog):
    def __init__(self, visible: bool = False):
        super().__init__(visible)
        self.position = Vector(200, 0)
        text_width = 150
        text_height = 40
        self.components = {
            'width_text': TextComponent("Width:", Vector(0, 0), Vector(text_width, text_height)),
            'width_input': Input(Vector(text_width, 0), Vector(300, text_height), has_focus=True),

            'height_text': TextComponent("Height:",
                                         Vector(0, -text_height), Vector(text_width, text_height)),
            'height_input': Input(Vector(text_width, -text_height), Vector(300, text_height)),

            'name_text': TextComponent("Name:",
                                       Vector(0, -text_height * 2), Vector(text_width, text_height)),
            'name_input': Input(Vector(text_width, -text_height * 2), Vector(300, text_height)),

            'submit_button': TextComponent("Create",
                                           Vector(0, -text_height * 3), Vector(text_width, text_height)),
            'cancel_button': TextComponent("Cancel", Vector(text_width, -text_height * 3),
                                           Vector(text_width, text_height))
        }

    def open(self, game_state):
        super().open(game_state)
        self.components['width_input'].text = ""
        self.components['height_input'].text = ""
        self.components['name_input'].text = ""

    def render(self):
        if self.visible:
            for component in self.components:
                self.components[component].render(self.position)

    def update(self, game_state):
        super().update(game_state)

        for component in self.components:
            if 'input' in component:
                self.components[component].add_text(game_state.key_presses)

        def submit():
            try:
                new_width = int(self.components['width_input'].text)
                new_height = int(self.components['height_input'].text)
            except Exception as e:
                print(e)
                return
            game_state.tile_map.new(game_state, MAPS_PATH + self.components['name_input'].text + '.map', new_width,
                                    new_height)
            self.visible = False

        def cancel():
            self.visible = False

        handlers = {
            'width_input': None,
            'height_input': None,
            'name_input': None,
            'submit_button': submit,
            'cancel_button': cancel
        }

        for click in game_state.mouse_clicks.copy():
            for component in handlers:
                copy_click = MouseClick()
                copy_click.button = click.button
                copy_click.position = click.position - self.position

                if self.components[component].is_clicked(copy_click):
                    if 'input' in component:
                        self.give_exclusive_focus(component)
                    else:
                        handlers[component]()
                    game_state.mouse_clicks.remove(click)

    def give_exclusive_focus(self, component: str):
        for other_component in self.components:
            if component == other_component:
                continue
            if 'input' in other_component:
                self.components[other_component].has_focus = False


class LoadMapDialog(Dialog):
    def __init__(self, visible: bool = False):
        super().__init__(visible)
        self.maps: List[TextComponent] = []
        self.cancel_button: TextComponent = None

        current_index, height = self.refresh_maps()
        self.update_cancel_button(current_index, height)

    def refresh_maps(self):
        self.maps = []
        current_index = 0
        height = 50
        for file in os.listdir(MAPS_PATH):
            if '.map' in file:
                text_component = TextComponent(file, Vector(150, 100 - height * current_index), Vector(300, height))
                self.maps.append(text_component)
                current_index += 1
        return current_index, height

    def update_cancel_button(self, current_index, height):
        self.cancel_button = TextComponent("Cancel", Vector(150, 100 - height * current_index), Vector(200, height))

    def open(self, game_state):
        super().open(game_state)
        current_index, height = self.refresh_maps()
        self.update_cancel_button(current_index, height)

    def update(self, game_state):
        super().update(game_state)

        for click in game_state.mouse_clicks.copy():
            copy_click = MouseClick()
            copy_click.button = click.button
            copy_click.position = click.position - self.position

            if self.cancel_button.is_clicked(copy_click):
                self.visible = False
                game_state.mouse_clicks.remove(click)
                return
            for tile_map in self.maps:
                if tile_map.is_clicked(copy_click):
                    game_state.tile_map.load(game_state, MAPS_PATH + tile_map.text)
                    self.visible = False
                    game_state.mouse_clicks.remove(click)
                    return

    def render(self):
        if self.visible:
            for tile_map in self.maps:
                tile_map.render(self.position)
            self.cancel_button.render(self.position)
