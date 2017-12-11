from enum import Enum


class GameMode(Enum):
    NORMAL = 0
    TEST = 1
    BUILDING = 2


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
