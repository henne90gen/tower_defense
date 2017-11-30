from tile_map import TileMap, Textures
from user_interface import HUD


class GameState:
    def __init__(self):
        self.tile_map: TileMap = TileMap()
        self.tile_map.load("./res/basic.map")
        self.hud: HUD = HUD()
        self.textures = Textures()
