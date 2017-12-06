import pygame
import sys


class KeyPresses:
    def __init__(self):
        self.left = False
        self.right = False
        self.up = False
        self.down = False
        self.back_space = False
        self.text = ""


class MouseClick:
    def __init__(self):
        self.position = Vector(0, 0)
        self.button = None

    def __eq__(self, other):
        if type(other) != MouseClick:
            return False
        return self.position == other.position and self.button == other.button


class Vector:
    def __init__(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y

    def __str__(self):
        return '({}, {})'.format(self.x, self.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not self.__eq__(other)

    def __add__(self, other):
        if type(other) == tuple:
            return self.__radd__(other)
        return Vector(self.x + other.x, self.y + other.y)

    def __radd__(self, other):
        return Vector(self.x + other[0], self.y + other[1])

    def __sub__(self, other):
        if type(other) == tuple:
            return Vector(self.x - other[0], self.y - other[1])
        return Vector(self.x - other.x, self.y - other.y)

    def __rsub__(self, other):
        return Vector(other[0] - self.x, other[1] - self.y)

    def __mul__(self, other):
        if type(other) == float or type(other) == int:
            return Vector(self.x * other, self.y * other)


def rect_contains_point(point: Vector, rect_position: Vector, rect_size: Vector):
    """
    :param point:
    :param rect_position: top left position of rectangle
    :param rect_size:
    :return:
    """
    if rect_position.x < point.x < rect_position.x + rect_size.x:
        if rect_position.y - rect_size.y < point.y < rect_position.y:
            return True
    return False


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
            mouse_click.position = event.pos
            mouse_click.button = event.button
            game_state.mouse_clicks.append(mouse_click)
        elif event.type == pygame.MOUSEMOTION:
            game_state.mouse_position = event.pos

    return screen, game_state
