from typing import List

import pygame

from tile_map import MouseClick


class Button:
    def __init__(self, text: str, rect: pygame.Rect):
        self.text = text
        self.rect = rect

    def render(self, screen: pygame.Surface):
        button_surface = pygame.Surface(self.rect.size)

        color = (255, 0, 255)
        button_surface.fill(color)

        my_font = pygame.font.SysFont('Comic Sans MS', 35)
        text_surface: pygame.Surface = my_font.render(self.text, True, (0, 0, 0))
        x_offset = (self.rect.width - text_surface.get_width()) / 2
        y_offset = (self.rect.height - text_surface.get_height()) / 2
        button_surface.blit(text_surface, (x_offset, y_offset))

        screen.blit(button_surface, (self.rect.left, self.rect.top))

    def is_clicked(self, mouse_click: MouseClick):
        return self.rect.contains(pygame.Rect(mouse_click.pos, (0, 0)))


class HUD:
    def __init__(self):
        self.save_button: Button = Button("Save", pygame.Rect(0, 0, 100, 50))

    def update(self, game_state, mouse_clicks: List[MouseClick]):
        for click in mouse_clicks.copy():
            if self.save_button.is_clicked(click):
                game_state.tile_map.save()
                mouse_clicks.remove(click)

    def render(self, screen: pygame.Surface):
        self.save_button.render(screen)
