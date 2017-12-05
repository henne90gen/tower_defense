from datetime import datetime

import pyglet

from game_state import GameState
from helper import poll_events

window = pyglet.window.Window()
window.set_caption("Tower Defense")

label = pyglet.text.Label('Hello, world',
                          font_name='Times New Roman',
                          font_size=36,
                          x=window.width // 2, y=window.height // 2,
                          anchor_x='center', anchor_y='center')


@window.event
def on_key_press(symbol, modifiers):
    print(symbol, modifiers)


@window.event
def on_mouse_press(x, y, button, modifiers):
    print(x, y, button, modifiers)


@window.event
def on_draw():
    window.clear()
    label.draw()


pyglet.app.run()

# pygame.init()
# pygame.font.init()
#
# size = 1280, 720
# window_parameters = pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE
# screen = pygame.display.set_mode(size, window_parameters)
# pygame.display.set_caption("Tower Defense")
#
# game_state = GameState()
#
# timer = datetime.now()
#
# while True:
#     start = datetime.now().timestamp()
#
#     screen.fill((0, 0, 0))
#     screen, game_state = poll_events(screen, game_state, window_parameters)
#
#     game_state.update(screen)
#
#     game_state.hud.update(game_state)
#     game_state.entity_manager.update(game_state)
#     game_state.tile_map.update(game_state)
#
#     game_state.tile_map.render(game_state, screen)
#     game_state.entity_manager.render(game_state, screen)
#     game_state.hud.render(screen)
#
#     pygame.display.flip()
#
#     end = datetime.now().timestamp()
#     fps = 1 / (end - start)
#     now = datetime.now()
#     if (now - timer).total_seconds() > 0.075:
#         pygame.display.set_caption("Tower Defense (" + str(fps) + "fps)")
#         timer = now
