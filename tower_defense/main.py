import sys
from typing import List

from datetime import datetime
import pygame

from game_state import GameState
from helper import KeyPresses, MouseClick, poll_events

pygame.init()
pygame.font.init()

size = 1280, 720
window_parameters = pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE
screen = pygame.display.set_mode(size, window_parameters)
pygame.display.set_caption("Tower Defense")

game_state = GameState()

timer = datetime.now()

while True:
    start = datetime.now().timestamp()

    screen.fill((0, 0, 0))
    screen, game_state = poll_events(screen, game_state, window_parameters)

    game_state.update(screen)

    game_state.hud.update(game_state)
    game_state.entity_manager.update(game_state)
    game_state.tile_map.update(game_state)

    game_state.tile_map.render(game_state, screen)
    game_state.entity_manager.render(game_state, screen)
    game_state.hud.render(screen)

    pygame.display.flip()

    end = datetime.now().timestamp()
    fps = 1 / (end - start)
    now = datetime.now()
    if (now - timer).total_seconds() > 0.075:
        pygame.display.set_caption("Tower Defense (" + str(fps) + "fps)")
        timer = now
