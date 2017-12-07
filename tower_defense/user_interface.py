import os
from enum import Enum, auto
from typing import List

import pyglet

from game_types import GameMode
from helper import MouseClick, KeyPresses, Vector, rect_contains_point

MAPS_PATH = './res/maps/'


class TextComponent:
    class TextAlignment(Enum):
        CENTER = auto()
        LEFT = auto()

    def __init__(self, text: str, position: Vector, size: Vector, font_size: int = 25,
                 text_alignment: TextAlignment = TextAlignment.CENTER,
                 visible: bool = True):
        self.text = text
        self.position = position
        self.size = size
        self.label = pyglet.text.Label(self.text,
                                       font_name='DejaVuSans',
                                       font_size=font_size,
                                       color=(255, 0, 255, 255),
                                       width=self.size.x, height=self.size.y,
                                       anchor_x='center', anchor_y='center')
        self.visible = visible
        self.text_alignment = text_alignment

    def toggle_visibility(self):
        self.visible = not self.visible

    def is_clicked(self, mouse_click: MouseClick) -> bool:
        if not self.visible:
            return False
        # print(self.text)
        # print(self.position)
        # print(self.size)
        # print(mouse_click.position)
        return rect_contains_point(mouse_click.position, self.position, self.size)

    def render(self, offset: Vector):
        if not self.visible:
            return

        pos = self.position + offset
        self.label.begin_update()
        self.label.x = pos.x + self.size.x / 2
        self.label.y = pos.y - self.size.y / 2
        self.label.text = self.text
        self.label.end_update()

        bottom_right = Vector(pos.x + self.size.x, pos.y - self.size.y)
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, (
            'v2f', [pos.x, pos.y, bottom_right.x, pos.y, bottom_right.x, bottom_right.y, pos.x, bottom_right.y]))

        self.label.draw()


class Input(TextComponent):
    def __init__(self, position: Vector, size: Vector, font_size: int = 25, visible: bool = True,
                 has_focus: bool = False):
        super().__init__("", position, size, font_size, TextComponent.TextAlignment.LEFT, visible)
        self.has_focus = has_focus

    def is_clicked(self, mouse_click):
        if super().is_clicked(mouse_click):
            self.has_focus = True
            return True
        return False

    def add_text(self, key_presses: KeyPresses):
        if not self.has_focus:
            return

        if key_presses.back_space:
            self.text = self.text[:-1]
        else:
            self.text = self.text + key_presses.text


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


class HUD:
    def __init__(self):
        button_height = 50
        size = Vector(150, button_height)
        self.components = {
            'menu_button': TextComponent("Menu", Vector(0, 0), size),
            'mode_button': TextComponent("", Vector(0, -button_height), size, visible=False),
            'new_button': TextComponent("New", Vector(0, -2 * button_height), size, visible=False),
            'save_button': TextComponent("Save", Vector(0, -3 * button_height), size, visible=False),
            'load_button': TextComponent("Load", Vector(0, -4 * button_height), size, visible=False)
        }
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
                self.toggle_menu()

            def mode():
                if game_state.mode == GameMode.NORMAL:
                    game_state.mode = GameMode.TEST
                    self.components['mode_button'].text = "TEST"
                elif game_state.mode == GameMode.TEST:
                    game_state.mode = GameMode.NORMAL
                    self.components['mode_button'].text = game_state.mode.name
                self.toggle_menu()

            def save():
                game_state.tile_map.save()
                self.toggle_menu()

            def new():
                self.toggle_menu()
                self.new_dialog.open(game_state)

            def load():
                self.toggle_menu()
                self.load_dialog.open(game_state)

            handlers = {
                'menu_button': menu,
                'mode_button': mode,
                'save_button': save,
                'new_button': new,
                'load_button': load
            }

            if self.components['mode_button'].text == "":
                self.components['mode_button'].text = game_state.mode.name

            for click in game_state.mouse_clicks.copy():
                for component in handlers:
                    copy_click = MouseClick()
                    copy_click.button = click.button
                    copy_click.position = click.position - self.offset
                    if self.components[component].is_clicked(copy_click):
                        handlers[component]()
                        game_state.mouse_clicks.remove(click)

    def toggle_menu(self):
        self.components['mode_button'].toggle_visibility()
        self.components['new_button'].toggle_visibility()
        self.components['save_button'].toggle_visibility()
        self.components['load_button'].toggle_visibility()

    def render(self):
        for component in self.components:
            self.components[component].render(self.offset)

        self.new_dialog.render()
        self.load_dialog.render()
