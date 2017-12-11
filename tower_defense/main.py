import pyglet

from game_state import GameState
from helper import MouseClick, Vector

window = pyglet.window.Window(width=1280, height=720, resizable=True)
window.set_caption("Tower Defense")
game_state = GameState()
game_state.init()

pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)


def handle_key(symbol, modifiers, key_down):
    print("KeyEvent", key_down, symbol, modifiers)

    kp = game_state.key_presses

    if symbol == pyglet.window.key.W:
        kp.up = key_down
    elif symbol == pyglet.window.key.S:
        kp.down = key_down
    elif symbol == pyglet.window.key.A:
        kp.left = key_down
    elif symbol == pyglet.window.key.D:
        kp.right = key_down

    if symbol == pyglet.window.key.BACKSPACE:
        kp.back_space = key_down
    elif key_down:
        text = pyglet.window.key.symbol_string(symbol)
        if len(text[1:]) > 0 and text[1:] in "0123456789":
            # numbers come out as e.g. '_1'
            text = text[1:]
        if 'NUM_' in text:
            # numpad keys come out as e.g. 'NUM_1'
            text = text[4:]
        kp.text = kp.text + text.lower()

    game_state.key_presses = kp


@window.event
def on_key_press(symbol, modifiers):
    handle_key(symbol, modifiers, True)


@window.event
def on_key_release(symbol, modifiers):
    handle_key(symbol, modifiers, False)


@window.event
def on_mouse_press(x, y, button, modifiers):
    print("MousePress", x, y, button, modifiers)
    mouse_click = MouseClick()
    mouse_click.position = Vector(x, y)
    mouse_click.button = button
    game_state.mouse_clicks.append(mouse_click)


@window.event
def on_draw(value=None):
    window.clear()

    game_state.update(Vector(*window.get_size()))

    game_state.hud.update(game_state)
    game_state.entity_manager.update(game_state)
    game_state.building_manager.update(game_state)
    game_state.tile_map.update(game_state)

    game_state.tile_map.render(game_state)
    game_state.entity_manager.render(game_state)
    game_state.building_manager.render(game_state)
    game_state.hud.render()

    game_state.clean_up()


pyglet.clock.schedule_interval(on_draw, 1 / 60.0)
pyglet.clock.set_fps_limit(60)
pyglet.app.run()
