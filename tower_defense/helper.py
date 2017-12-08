import math
import sys
from typing import Callable

import pygame


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

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

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


def process_clicks(game_state, processor: Callable[[object, MouseClick], bool], offset: Vector = Vector()):
    for click in game_state.mouse_clicks.copy():
        offset_click = MouseClick()
        offset_click.button = click.button
        offset_click.position = click.position + offset
        if processor(game_state, offset_click):
            game_state.mouse_clicks.remove(click)
