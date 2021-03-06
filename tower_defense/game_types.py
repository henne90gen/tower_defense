from enum import Enum


class GameMode(Enum):
    MAIN_MENU = 0
    EDITOR = 1
    GAME = 2
    MAP_CHOICE_EDITOR = 3
    MAP_CHOICE_GAME = 4


class TileType(Enum):
    BUILDING_GROUND = 0
    PATH = 1
    START = 2
    FINISH = 3


class EntityType(Enum):
    LARGE_BOULDER = 0
    SMALL_BOULDER = 1
    MINERAL = 2


class BuildingType(Enum):
    LASER = 0
    HAMMER = 1
    DRILL = 2
    PLATFORM = 3


class BulletType(Enum):
    STANDARD = 0
    DYNAMITE = 1
