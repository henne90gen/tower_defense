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
    BOULDER = 0
    MINERAL = 1


class BuildingType(Enum):
    LASER = 0
    CATAPULT = 1
    DRILL = 2


class BulletType(Enum):
    STANDARD = 0
    DYNAMITE = 1
