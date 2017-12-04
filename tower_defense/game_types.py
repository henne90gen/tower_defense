from enum import Enum


class GameMode(Enum):
    EDITOR = 0
    ENTITY_PLACEMENT = 1


class TileType(Enum):
    BUILDING_GROUND = 0
    PATH = 1
    START = 2
    FINISH = 3


class EntityType(Enum):
    WARRIOR = 0
