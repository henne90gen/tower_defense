import os
import pickle
from enum import Enum
from typing import List, Dict

import pygame


class KeyPresses:
    def __init__(self):
        self.left = False
        self.right = False
        self.up = False
        self.down = False


class MouseClick:
    def __init__(self):
        self.pos = (0, 0)
        self.button = None


class Textures:
    def __init__(self):
        self.tiles: Dict[TileType, pygame.Surface] = {}
        self.tiles[TileType.GRASS] = pygame.image.load('./res/grass.jpg')
        self.tiles[TileType.SAND] = pygame.image.load('./res/sand.jpg')


class TileType(Enum):
    GRASS = 0
    SAND = 1


class Tile:
    def __init__(self, rect: pygame.Rect, tile_type: TileType):
        self.rect: pygame.Rect = rect
        self.tile_type = tile_type

    def __eq__(self, other):
        if type(other) != Tile:
            return False
        return self.rect == other.rect and self.tile_type == other.tile_type

    def __str__(self):
        return "Tile: " + str(self.rect) + " - " + str(self.tile_type)

    def next_type(self):
        type_list = list(TileType)
        index = type_list.index(self.tile_type)
        index += 1

        if index >= len(type_list):
            return False

        self.tile_type = type_list[index]
        return True

    def render(self, screen: pygame.Surface, x_offset: int, y_offset: int, textures: Dict[TileType, pygame.Surface]):
        x = self.rect.left + x_offset
        y = self.rect.top + y_offset
        area = pygame.Rect(0, 0, self.rect.width, self.rect.height)
        screen.blit(textures[self.tile_type], (x, y), area=area)


class TileMap:
    def __init__(self):
        self.path = ""
        self.x_offset = 0
        self.y_offset = 0
        self.cursor_position = (0, 0)
        self.tile_width = 100
        self.tile_height = 100
        self.tiles: List[Tile] = []

    def load(self, path: str):
        self.path = path.strip()
        if os.path.isfile(path):
            with open(path, "rb") as f:
                self.tiles = pickle.load(f)

    def save(self):
        if len(self.path) > 0:
            with open(self.path, "wb") as f:
                pickle.dump(self.tiles, f)
                print("Saved tile map")

    def to_tile_map_space(self, pos: (int, int)) -> (int, int):
        return pos[0] - self.x_offset, pos[1] - self.y_offset

    def render(self, screen: pygame.Surface, textures: Textures):
        for tile in self.tiles:
            tile.render(screen, self.x_offset, self.y_offset, textures.tiles)

        x, y = self.cursor_position
        x += self.x_offset
        y += self.y_offset
        rect = pygame.Rect((x - 5, y - 5), (10, 10))
        screen.fill((0, 255, 255), rect)

    def update(self, key_presses: KeyPresses, mouse_position: (int, int), mouse_clicks: List[MouseClick]):
        scroll_speed = 5
        if key_presses.up:
            self.y_offset += scroll_speed
        if key_presses.down:
            self.y_offset -= scroll_speed
        if key_presses.left:
            self.x_offset += scroll_speed
        if key_presses.right:
            self.x_offset -= scroll_speed

        self.cursor_position = self.to_tile_map_space(mouse_position)

        for click in mouse_clicks:
            found_tile = False
            for tile in self.tiles.copy():
                pos = self.to_tile_map_space(click.pos)
                if tile.rect.contains(pygame.Rect(pos, (0, 0))):
                    found_tile = True
                    if not tile.next_type():
                        self.tiles.remove(tile)

            if not found_tile:
                x = int(self.cursor_position[0] / self.tile_width) * self.tile_width
                y = int(self.cursor_position[1] / self.tile_height) * self.tile_height
                rect = pygame.Rect((x, y), (self.tile_width, self.tile_height))
                tile_type = TileType(0)
                self.tiles.append(Tile(rect, tile_type))
