from enum import Enum


class GameMode(Enum):
    EDITOR = 0
    ENTITY_PLACEMENT = 1


class TileType(Enum):
    GRASS = 0
    SAND = 1


class EntityType(Enum):
    WARRIOR = 0
