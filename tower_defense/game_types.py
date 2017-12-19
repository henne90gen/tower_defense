from enum import Enum


class GameMode(Enum):
    MAIN_MENU = 0
    EDITOR = 1
    MAP_CHOICE = 2
    GAME = 3


class TileType(Enum):
    BUILDING_GROUND = 0
    PATH = 1
    START = 2
    FINISH = 3


class EntityType(Enum):
    WARRIOR = 0


class BuildingType(Enum):
    TOWER = 0


class BulletType(Enum):
    STANDARD = 0
