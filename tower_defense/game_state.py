from tile_map import TileMap, Textures
from user_interface import HUD
from entity_manager import EntityManager


class GameState:
    def __init__(self):
        self.tile_map: TileMap = TileMap()
        self.tile_map.load("./res/maps/basic.map")

        self.hud: HUD = HUD()

        self.textures: Textures = Textures()

        self.entity_manager: EntityManager = EntityManager()
