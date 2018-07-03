from datetime import datetime

import pyglet

# using explicit import to make pyinstaller work
from tower_defense import game_state
from tower_defense import helper
from tower_defense import hot_reload

module_whitelist = ['helper', 'graphics', 'game_types', 'game_state',
                    'user_interface.menu', 'user_interface.components',
                    'user_interface.dialogs', 'user_interface.user_interface',
                    'tiles.tile_map', 'tiles.tile',
                    'entities.bullet', 'entities.entity_manager', 'entities.entity',
                    'buildings.building_manager', 'buildings.building']

num_frames = 0
start_time = datetime.now()

window = pyglet.window.Window(width=1280, height=720, resizable=True)
window.set_caption("Tower Defense")

gs = game_state.GameState()
gs.init()

pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)


def handle_key(symbol, modifiers, key_down):
    print("KeyEvent", key_down, symbol, modifiers)

    kp = gs.key_presses

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
        if text[1:] and text[1:] in "0123456789":
            # numbers come out as e.g. '_1'
            text = text[1:]
        if 'NUM_' in text:
            # numpad keys come out as e.g. 'NUM_1'
            text = text[4:]
        kp.text = kp.text + text.lower()

    gs.key_presses = kp


def show_average_time():
    global num_frames, start_time
    num_frames += 1
    end = datetime.now()
    diff = end - start_time
    average = diff.total_seconds() * 1000.0 / num_frames
    average_string = '%.5f' % average
    window.set_caption("Tower Defense " + str(average_string))

    if diff.total_seconds() > 1:
        start_time = end
        num_frames = 0


@window.event
def on_key_press(symbol, modifiers):
    handle_key(symbol, modifiers, True)


@window.event
def on_key_release(symbol, modifiers):
    handle_key(symbol, modifiers, False)


@window.event
def on_mouse_motion(x, y, dx, dy):
    gs.mouse_position = helper.Vector(x, y)


@window.event
def on_mouse_press(x, y, button, modifiers):
    print("MousePress", x, y, button, modifiers)
    mouse_click = helper.MouseClick()
    mouse_click.position = helper.Vector(x, y)
    mouse_click.button = button
    gs.mouse_clicks.append(mouse_click)


@window.event
def on_draw(_=None):
    whitelist = list(map(lambda m: f'tower_defense.{m}', module_whitelist))
    hot_reload.reload_all(whitelist, debug=False)

    window.clear()

    gs.tick(window)

    gs.clean_up()

    show_average_time()


pyglet.clock.schedule_interval(on_draw, 1 / 120.0)
pyglet.clock.set_fps_limit(120)
pyglet.app.run()
