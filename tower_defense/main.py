import sys
from typing import List

from datetime import datetime
import pygame

from game_state import GameState
from tile_map import KeyPresses, MouseClick

pygame.init()
pygame.font.init()

size = width, height = 1280, 720
window_parameters = pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE
screen = pygame.display.set_mode(size, window_parameters)
pygame.display.set_caption("Tower Defense")

key_presses = KeyPresses()
mouse_position = (0, 0)

game_state = GameState()


def handle_keypress(event, kp: KeyPresses, is_key_down: bool):
    if event.key == pygame.K_w:
        kp.up = is_key_down
    elif event.key == pygame.K_s:
        kp.down = is_key_down
    elif event.key == pygame.K_a:
        kp.left = is_key_down
    elif event.key == pygame.K_d:
        kp.right = is_key_down

    if 'unicode' in event.dict:
        kp.text = kp.text + event.unicode
    if not is_key_down:
        kp.text = ""

    return kp


def poll_events() -> (KeyPresses, List[MouseClick]):
    global size, width, height, screen, key_presses, mouse_position

    mouse_clicks = []

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            sys.exit()
        elif event.type == pygame.VIDEORESIZE:
            size = event.size
            width = event.w
            height = event.h
            screen = pygame.display.set_mode(size, window_parameters)
            pygame.display.flip()
        elif event.type == pygame.KEYDOWN:
            key_presses = handle_keypress(event, key_presses, True)
        elif event.type == pygame.KEYUP:
            key_presses = handle_keypress(event, key_presses, False)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_click = MouseClick()
            mouse_click.pos = event.pos
            mouse_click.button = event.button
            mouse_clicks.append(mouse_click)
        elif event.type == pygame.MOUSEMOTION:
            mouse_position = event.pos

    return key_presses, mouse_clicks, mouse_position


timer = datetime.now()

while True:
    start = datetime.now().timestamp()

    screen.fill((0, 0, 0))
    key_presses, mouse_clicks, mouse_position = poll_events()

    game_state.hud.update(game_state, key_presses, mouse_clicks)
    game_state.tile_map.update(screen, key_presses, mouse_clicks, mouse_position)

    game_state.tile_map.render(screen, game_state.textures)
    game_state.hud.render(screen)

    pygame.display.flip()

    end = datetime.now().timestamp()
    fps = 1 / (end - start)
    now = datetime.now()
    if (now - timer).total_seconds() > 0.075:
        pygame.display.set_caption("Tower Defense (" + str(fps) + "fps)")
        timer = now
