import math
from typing import Callable, Tuple

import os


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
        self.position = Vector()
        self.button = None

    def __eq__(self, other):
        if type(other) != MouseClick:
            return False
        return self.position == other.position and self.button == other.button


class Vector:
    def __init__(self, x: float = 0, y: float = 0, point: Tuple[float, float] = None) -> None:
        if point is not None:
            self.x = point[0]
            self.y = point[1]
        else:
            self.x = x
            self.y = y

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def angle(self):
        return math.atan2(self.y, self.x)

    def copy(self):
        return Vector(self.x, self.y)

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

    def __truediv__(self, other):
        if type(other) == float or type(other) == int:
            return Vector(self.x / other, self.y / other)

    def __floordiv__(self, other):
        if type(other) == float or type(other) == int:
            return Vector(self.x // other, self.y // other)


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


def constrain_rect_to_bounds(window_size: Vector, position: Vector, size: Vector) -> Vector:
    copy = position.copy()
    screen_width_half = window_size.x / 2
    screen_height_half = window_size.y / 2
    if copy.x > screen_width_half:
        copy.x = screen_width_half
    elif copy.x < -(size.x - screen_width_half):
        copy.x = -(size.x - screen_width_half)
    if copy.y > screen_height_half:
        copy.y = screen_height_half
    elif copy.y < -(size.y - screen_height_half):
        copy.y = -(size.y - screen_height_half)
    return copy


def process_clicks(game_state, processor: Callable[[object, MouseClick], bool], map_to_world_space: bool = True,
                   offset: Vector = Vector()):
    for click in game_state.mouse_clicks.copy():
        copy_click = MouseClick()
        copy_click.button = click.button
        if map_to_world_space:
            copy_click.position = game_state.window_to_world_space(
                click.position)
        else:
            copy_click.position = click.position - offset
        if processor(game_state, copy_click):
            game_state.mouse_clicks.remove(click)


def maps_list(maps_path: str):
    maps = []
    for file in os.listdir(maps_path):
        if '.map' in file:
            maps.append(file)
    return maps


def resolve_relative_path(path_func):
    def wrapper():
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), path_func())
    return wrapper


@resolve_relative_path
def get_res_path():
    return "res"


@resolve_relative_path
def get_maps_path():
    return os.path.join(get_res_path(), "maps")
