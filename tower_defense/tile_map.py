import os
import pickle
from typing import List, Dict

import pygame

from game_types import TileType
from graphics import Textures
from helper import KeyPresses, MouseClick


class Tile:
    def __init__(self, rect: pygame.Rect, tile_type: TileType):
        self.rect: pygame.Rect = rect
        self.tile_type = tile_type
        self.direction = (0, 0)

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
        self.border_width = 50
        self.x_offset = self.border_width * 2
        self.y_offset = self.border_width * 2
        self.cursor_position = (0, 0)
        self.tile_width = 100
        self.tile_height = 100
        self.max_tiles_x = 10
        self.max_tiles_y = 10
        self.tiles: List[Tile] = []

    def new(self, path: str, width: int, height: int):
        self.path = path.strip()
        self.tiles = []
        self.max_tiles_x = width
        self.max_tiles_y = height
        self.save()

    def load(self, path: str):
        self.path = path.strip()
        if os.path.isfile(self.path):
            with open(self.path, "rb") as f:
                self.tiles, self.max_tiles_x, self.max_tiles_y = pickle.load(f)
                print("Loaded tile map", self.path)

    def save(self):
        if len(self.path) > 0:
            with open(self.path, "wb") as f:
                pickle.dump((self.tiles, self.max_tiles_x, self.max_tiles_y), f)
                print("Saved tile map", self.path)

    def to_tile_map_space(self, pos: (int, int)) -> (int, int):
        return pos[0] - self.x_offset, pos[1] - self.y_offset

    def render_cursor(self, screen: pygame.Surface):
        x, y = self.cursor_position
        x += self.x_offset
        y += self.y_offset
        rect = pygame.Rect((x - 5, y - 5), (10, 10))
        screen.fill((0, 255, 255), rect)

    def render_border(self, screen: pygame.Surface):
        white = (255, 255, 255)

        surface_width = self.tile_map_width + self.border_width * 2
        surface_height = self.tile_map_height + self.border_width * 2
        border_surface = pygame.Surface((surface_width, surface_height))

        top_width = self.tile_map_width + self.border_width
        top_rect = pygame.Rect((self.border_width, 0), (top_width, self.border_width))
        border_surface.fill(white, top_rect)

        right_x = self.tile_map_width + self.border_width
        right_height = self.tile_map_height + self.border_width
        right_rect = pygame.Rect((right_x, self.border_width), (self.border_width, right_height))
        border_surface.fill(white, right_rect)

        bottom_y = self.tile_map_height + self.border_width
        bottom_width = self.tile_map_width + self.border_width
        bottom_rect = pygame.Rect((0, bottom_y), (bottom_width, self.border_width))
        border_surface.fill(white, bottom_rect)

        left_height = self.tile_map_height + self.border_width
        left_rect = pygame.Rect((0, 0), (self.border_width, left_height))
        border_surface.fill(white, left_rect)

        screen.blit(border_surface, (self.x_offset - self.border_width, self.y_offset - self.border_width))

    @property
    def tile_map_width(self):
        return self.tile_width * self.max_tiles_x

    @property
    def tile_map_height(self):
        return self.tile_height * self.max_tiles_y

    def is_on_tile_map(self, pos: (int, int)):
        x, y = pos
        return 0 < x < self.tile_map_width and 0 < y < self.tile_map_height

    def render(self, screen: pygame.Surface, textures: Textures):
        self.render_border(screen)

        for tile in self.tiles:
            tile.render(screen, self.x_offset, self.y_offset, textures.tiles)

    def update(self, screen: pygame.Surface, key_presses: KeyPresses, mouse_clicks: List[MouseClick],
               mouse_position: (int, int)):
        scroll_speed = 5
        if key_presses.up:
            self.y_offset += scroll_speed
        if key_presses.down:
            self.y_offset -= scroll_speed
        if key_presses.left:
            self.x_offset += scroll_speed
        if key_presses.right:
            self.x_offset -= scroll_speed

        self.x_offset, self.y_offset = self.constrain_to_bounds(screen, self.x_offset, self.y_offset,
                                                                self.tile_map_width, self.tile_map_height)

        self.cursor_position = self.to_tile_map_space(mouse_position)

        for click in mouse_clicks:
            pos = self.to_tile_map_space(click.pos)
            if not self.is_on_tile_map(pos):
                continue

            found_tile = False
            for tile in self.tiles.copy():
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

    @staticmethod
    def constrain_to_bounds(screen, x, y, width, height) -> (int, int):
        screen_width_half = screen.get_width() / 2
        screen_height_half = screen.get_height() / 2
        if x > screen_width_half:
            x = screen_width_half
        elif x < -(width - screen_width_half):
            x = -(width - screen_width_half)
        if y > screen_height_half:
            y = screen_height_half
        elif y < -(height - screen_height_half):
            y = -(height - screen_height_half)
        return x, y
