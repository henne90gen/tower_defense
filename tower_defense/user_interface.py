from enum import Enum, auto
from typing import List

import os
import pygame

from helper import MouseClick, KeyPresses

pygame.font.init()
font = pygame.font.SysFont('Comic Sans MS', 35)
MAPS_PATH = './res/maps/'


class TextComponent:
    class TextAlignment(Enum):
        CENTER = auto()
        LEFT = auto()

    def __init__(self, text: str, rect: pygame.Rect, text_alignment: TextAlignment = TextAlignment.CENTER,
                 visible: bool = True):
        self.text = text
        self.rect = rect
        self.visible = visible
        self.text_alignment = text_alignment

    def toggle_visibility(self):
        self.visible = not self.visible

    def is_clicked(self, mouse_click: MouseClick):
        return self.visible and self.rect.contains(pygame.Rect(mouse_click.pos, (0, 0)))

    def render(self, screen: pygame.Surface):
        if not self.visible:
            return
        button_surface = pygame.Surface(self.rect.size)

        color = (255, 100, 100)
        button_surface.fill(color)

        text_surface: pygame.Surface = font.render(self.text, True, (0, 0, 0))

        x_offset = 0
        y_offset = 0
        if self.text_alignment == TextComponent.TextAlignment.CENTER:
            x_offset = (self.rect.width - text_surface.get_width()) / 2
            y_offset = (self.rect.height - text_surface.get_height()) / 2
        elif self.text_alignment == TextComponent.TextAlignment.LEFT:
            x_offset = 10
            y_offset = (self.rect.height - text_surface.get_height()) / 2

        button_surface.blit(text_surface, (x_offset, y_offset))

        screen.blit(button_surface, (self.rect.left, self.rect.top))


class Input(TextComponent):
    def __init__(self, rect: pygame.Rect, visible: bool = True, has_focus: bool = False):
        super().__init__("", rect, TextComponent.TextAlignment.LEFT, visible)
        self.has_focus = has_focus

    def is_clicked(self, mouse_click):
        if super().is_clicked(mouse_click):
            self.has_focus = True
            return True
        return False

    def add_text(self, text: str):
        if not self.has_focus:
            return

        if u"\u0008" in text:
            self.text = self.text[:-1]
        else:
            self.text = self.text + text


class Dialog:
    def __init__(self, visible: bool):
        self.visible = visible

    def open(self):
        self.visible = True

    def render(self, screen: pygame.Surface):
        pass

    def update(self, game_state, key_presses: KeyPresses, mouse_clicks: List[MouseClick]):
        key_presses.up = key_presses.down = key_presses.left = key_presses.right = False


class NewMapDialog(Dialog):
    def __init__(self, visible: bool = False):
        super().__init__(visible)
        text_x = 150
        text_y = 150
        text_width = 100
        text_height = 50
        input_x = text_x + text_width
        self.components = {
            'width_text': TextComponent("Width:", pygame.Rect((text_x, text_y), (text_width, text_height))),
            'width_input': Input(pygame.Rect((input_x, text_y), (300, text_height)), has_focus=True),

            'height_text': TextComponent("Height:",
                                         pygame.Rect((text_x, text_y + text_height), (text_width, text_height))),
            'height_input': Input(pygame.Rect((input_x, text_y + text_height), (300, text_height))),

            'name_text': TextComponent("Name:",
                                       pygame.Rect((text_x, text_y + text_height * 2), (text_width, text_height))),
            'name_input': Input(pygame.Rect((input_x, text_y + text_height * 2), (300, text_height))),

            'submit_button': TextComponent("Create",
                                           pygame.Rect((text_x, text_y + text_height * 3), (text_width, text_height))),
            'cancel_button': TextComponent("Cancel", pygame.Rect((text_x + text_width, text_y + text_height * 3),
                                                                 (text_width, text_height)))
        }

    def render(self, screen: pygame.Surface):
        if self.visible:
            for component in self.components:
                self.components[component].render(screen)

    def update(self, game_state, key_presses: KeyPresses, mouse_clicks: List[MouseClick]):
        super().update(game_state, key_presses, mouse_clicks)

        for component in self.components:
            if 'input' in component:
                self.components[component].add_text(key_presses.text)

        def submit():
            try:
                new_width = int(self.components['width_input'].text)
                new_height = int(self.components['height_input'].text)
            except Exception as e:
                print(e)
                return
            game_state.tile_map.new(MAPS_PATH + self.components['name_input'].text + '.map', new_width, new_height)
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

        for click in mouse_clicks.copy():
            for component in handlers:
                if self.components[component].is_clicked(click):
                    if 'input' in component:
                        self.give_exclusive_focus(component)
                    else:
                        handlers[component]()
                    mouse_clicks.remove(click)

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
        current_index, height = self.refresh_maps()

        self.cancel_button = TextComponent("Cancel", pygame.Rect((150, 100 + height * current_index), (100, height)))

    def refresh_maps(self):
        current_index = 0
        height = 50
        for file in os.listdir(MAPS_PATH):
            if '.map' in file:
                text_component = TextComponent(file, pygame.Rect((150, 100 + height * current_index), (300, height)))
                self.maps.append(text_component)
                current_index += 1
        return current_index, height

    def update(self, game_state, key_presses: KeyPresses, mouse_clicks: List[MouseClick]):
        super().update(game_state, key_presses, mouse_clicks)

        current_index, height = self.refresh_maps()
        self.cancel_button = TextComponent("Cancel", pygame.Rect((150, 100 + height * current_index), (100, height)))

        for click in mouse_clicks:
            if self.cancel_button.is_clicked(click):
                self.visible = False
                mouse_clicks.remove(click)
                return
            for tile_map in self.maps:
                if tile_map.is_clicked(click):
                    game_state.tile_map.load(MAPS_PATH + tile_map.text)
                    self.visible = False
                    mouse_clicks.remove(click)
                    return

    def render(self, screen: pygame.Surface):
        if self.visible:
            for tile_map in self.maps:
                tile_map.render(screen)
            self.cancel_button.render(screen)


class HUD:
    def __init__(self):
        button_height = 50
        self.components = {
            'menu_button': TextComponent("Menu", pygame.Rect(0, 0, 100, button_height)),
            'new_button': TextComponent("New", pygame.Rect(0, button_height, 100, button_height), visible=False),
            'save_button': TextComponent("Save", pygame.Rect(0, 2 * button_height, 100, button_height), visible=False),
            'load_button': TextComponent("Load", pygame.Rect(0, 3 * button_height, 100, button_height), visible=False)
        }
        self.new_dialog: Dialog = NewMapDialog()
        self.load_dialog: Dialog = LoadMapDialog()

    def update(self, game_state, key_presses: KeyPresses, mouse_clicks: List[MouseClick]):
        if self.new_dialog.visible:
            self.new_dialog.update(game_state, key_presses, mouse_clicks)
        elif self.load_dialog.visible:
            self.load_dialog.update(game_state, key_presses, mouse_clicks)
        else:
            def save():
                game_state.tile_map.save()
                self.toggle_menu()

            def menu():
                self.toggle_menu()

            def new():
                self.toggle_menu()
                self.new_dialog.open()

            def load():
                self.toggle_menu()
                self.load_dialog.open()

            handlers = {
                'save_button': save,
                'menu_button': menu,
                'new_button': new,
                'load_button': load
            }

            for click in mouse_clicks.copy():
                for component in handlers:
                    if self.components[component].is_clicked(click):
                        handlers[component]()
                        mouse_clicks.remove(click)

    def toggle_menu(self):
        self.components['new_button'].toggle_visibility()
        self.components['save_button'].toggle_visibility()
        self.components['load_button'].toggle_visibility()

    def render(self, screen: pygame.Surface):
        for component in self.components:
            self.components[component].render(screen)

        self.new_dialog.render(screen)
        self.load_dialog.render(screen)
