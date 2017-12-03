import pygame
import sys


class KeyPresses:
    def __init__(self):
        self.left = False
        self.right = False
        self.up = False
        self.down = False
        self.text = ""


class MouseClick:
    def __init__(self):
        self.pos = (0, 0)
        self.button = None


def handle_keypress(event, kp: KeyPresses, is_key_down: bool):
    if event.key == pygame.K_w:
        kp.up = is_key_down
    elif event.key == pygame.K_s:
        kp.down = is_key_down
    elif event.key == pygame.K_a:
        kp.left = is_key_down
    elif event.key == pygame.K_d:
        kp.right = is_key_down

    if 'unicode' in event.dict and event.unicode not in kp.text:
        kp.text = kp.text + event.unicode

    return kp


def poll_events(screen: pygame.Surface, game_state: object, window_parameters) -> (pygame.Surface, object):

    game_state.mouse_clicks = []
    game_state.key_presses.text = ""

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            sys.exit()
        elif event.type == pygame.VIDEORESIZE:
            size = event.size
            screen = pygame.display.set_mode(size, window_parameters)
            pygame.display.flip()
        elif event.type == pygame.KEYDOWN:
            game_state.key_presses = handle_keypress(event, game_state.key_presses, True)
        elif event.type == pygame.KEYUP:
            game_state.key_presses = handle_keypress(event, game_state.key_presses, False)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_click = MouseClick()
            mouse_click.pos = event.pos
            mouse_click.button = event.button
            game_state.mouse_clicks.append(mouse_click)
        elif event.type == pygame.MOUSEMOTION:
            game_state.mouse_position = event.pos

    return screen, game_state
