from typing import List

import pygame

from tile_map import MouseClick, KeyPresses

pygame.font.init()
font = pygame.font.SysFont('Comic Sans MS', 35)


class Button:
    def __init__(self, text: str, rect: pygame.Rect, visible: bool = True):
        self.text = text
        self.rect = rect
        self.visible = visible

    def render(self, screen: pygame.Surface):
        if not self.visible:
            return
        button_surface = pygame.Surface(self.rect.size)

        color = (255, 0, 255)
        button_surface.fill(color)

        text_surface: pygame.Surface = font.render(self.text, True, (0, 0, 0))
        x_offset = (self.rect.width - text_surface.get_width()) / 2
        y_offset = (self.rect.height - text_surface.get_height()) / 2
        button_surface.blit(text_surface, (x_offset, y_offset))

        screen.blit(button_surface, (self.rect.left, self.rect.top))

    def is_clicked(self, mouse_click: MouseClick):
        return self.visible and self.rect.contains(pygame.Rect(mouse_click.pos, (0, 0)))

    def toggle_visibility(self):
        self.visible = not self.visible


class Input:
    def __init__(self, rect: pygame.Rect, visible: bool = True):
        self.text = ""
        self.rect = rect
        self.visible = visible
        self.has_focus = False

    def render(self, screen):
        if not self.visible:
            return
        button_surface = pygame.Surface(self.rect.size)

        color = (255, 255, 0)
        button_surface.fill(color)

        text_surface: pygame.Surface = font.render(self.text, True, (0, 0, 0))
        y_offset = (self.rect.height - text_surface.get_height()) / 2
        button_surface.blit(text_surface, (10, y_offset))

        screen.blit(button_surface, (self.rect.left, self.rect.top))

    def add_text(self, text):
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

    def update(self, game_state, key_presses: KeyPresses):
        pass


class NewMapDialog(Dialog):
    def __init__(self, visible: bool = False):
        super().__init__(visible)
        self.width_input = Input(pygame.Rect((150, 150), (300, 50)))
        self.width_input.has_focus = True
        # self.height_input = Input(pygame.Rect((100, 150), (300, 50)))

    def render(self, screen: pygame.Surface):
        if self.visible:
            self.width_input.render(screen)
            # self.height_input.render(screen)

    def update(self, game_state, key_presses: KeyPresses):
        if self.width_input.has_focus:
            self.width_input.add_text(key_presses.text)
            # if self.height_input.has_focus:
            #     self.height_input.add_text(key_presses.text)


class LoadMapDialog(Dialog):
    def __init__(self, visible: bool = False):
        super().__init__(visible)

    def render(self, screen: pygame.Surface):
        pass


class HUD:
    def __init__(self):
        button_height = 50
        self.menu_button = Button("Menu", pygame.Rect(0, 0, 100, button_height))
        self.new_button = Button("New", pygame.Rect(0, button_height, 100, button_height), False)
        self.save_button = Button("Save", pygame.Rect(0, 2 * button_height, 100, button_height), False)
        self.load_button = Button("Load", pygame.Rect(0, 3 * button_height, 100, button_height), False)
        self.new_dialog = NewMapDialog()
        self.load_dialog = LoadMapDialog()

    def update(self, game_state, key_presses: KeyPresses, mouse_clicks: List[MouseClick]):
        for click in mouse_clicks.copy():
            if self.save_button.is_clicked(click):
                game_state.tile_map.save()
                mouse_clicks.remove(click)
            if self.menu_button.is_clicked(click):
                self.toggle_menu()
            if self.new_button.is_clicked(click):
                self.toggle_menu()
                self.new_dialog.open()

        self.new_dialog.update(game_state, key_presses)
        self.load_dialog.update(game_state, key_presses)

    def toggle_menu(self):
        self.new_button.toggle_visibility()
        self.save_button.toggle_visibility()
        self.load_button.toggle_visibility()

    def render(self, screen: pygame.Surface):
        self.menu_button.render(screen)
        self.new_button.render(screen)
        self.save_button.render(screen)
        self.load_button.render(screen)
        self.new_dialog.render(screen)
        self.load_dialog.render(screen)
