import os
import pickle
from typing import List

import pygame

from game_types import TileType


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

    @property
    def is_walkable(self):
        return self.direction != (0, 0)

    def next_type(self):
        type_list = list(TileType)
        index = type_list.index(self.tile_type)
        index += 1

        if index >= len(type_list):
            index = 0

        self.tile_type = type_list[index]
        return True

    def render(self, game_state, screen: pygame.Surface):
        x = self.rect.left + game_state.world_offset_x
        y = self.rect.top + game_state.world_offset_y
        area = pygame.Rect(0, 0, self.rect.width, self.rect.height)
        screen.blit(game_state.textures.tiles[self.tile_type], (x, y), area=area)


class TileMap:
    def __init__(self):
        self.path = ""
        self.border_width = 50
        self.cursor_position = (0, 0)
        self.tile_width = 100
        self.tile_height = 100
        self.max_tiles_x = 10
        self.max_tiles_y = 10
        self.tiles: List[Tile] = []

    def generate_tiles(self):
        self.tiles = []
        for x in range(self.max_tiles_x):
            for y in range(self.max_tiles_y):
                tile = Tile(
                    pygame.Rect((x * self.tile_width, y * self.tile_height), (self.tile_width, self.tile_height)),
                    TileType.GRASS)
                self.tiles.append(tile)

    def new(self, path: str, width: int, height: int):
        self.path = path.strip()
        self.max_tiles_x = width
        self.max_tiles_y = height
        self.generate_tiles()
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

    def render_cursor(self, game_state, screen: pygame.Surface):
        x, y = self.cursor_position
        x += game_state.world_offset_x
        y += game_state.world_offset_y
        rect = pygame.Rect((x - 5, y - 5), (10, 10))
        screen.fill((0, 255, 255), rect)

    def render_border(self, game_state, screen: pygame.Surface):
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

        screen.blit(border_surface,
                    (game_state.world_offset_x - self.border_width, game_state.world_offset_y - self.border_width))

    @property
    def tile_map_width(self):
        return self.tile_width * self.max_tiles_x

    @property
    def tile_map_height(self):
        return self.tile_height * self.max_tiles_y

    def is_on_map(self, game_state, position: (int, int), pos_is_in_tile_map_space: bool = True):
        if not pos_is_in_tile_map_space:
            position = game_state.to_world_space(position)
        x, y = position
        return 0 < x < self.tile_map_width and 0 < y < self.tile_map_height

    def get_tile(self, game_state, position: (int, int), pos_is_in_tile_map_space: bool = True):
        if not pos_is_in_tile_map_space:
            position = game_state.to_world_space(position)

        for tile in self.tiles:
            if tile.rect.contains(pygame.Rect(position, (0, 0))):
                return tile

    def render(self, game_state, screen: pygame.Surface):
        self.render_border(game_state, screen)

        for tile in self.tiles:
            tile.render(game_state, screen)

    def update(self, game_state):
        mouse_position = game_state.mouse_position

        self.cursor_position = game_state.to_world_space(mouse_position)

        self.handle_clicks(game_state)

    def handle_clicks(self, game_state):
        if not game_state.editor_mode:
            return

        for click in game_state.mouse_clicks.copy():
            pos = game_state.to_world_space(click.pos)
            if not self.is_on_map(game_state, pos, True):
                continue

            for tile in self.tiles.copy():
                if tile.rect.contains(pygame.Rect(pos, (0, 0))):
                    tile.next_type()
                    self.calculate_directions(game_state)

    def calculate_directions(self, game_state):
        for tile in self.tiles:
            if tile.tile_type == TileType.GRASS:
                tile.direction = (0, 0)
            elif tile.tile_type == TileType.SAND:
                x, y = tile.rect.left, tile.rect.top
                if self.get_tile(game_state, (x + self.tile_width, y)).is_walkable:
                    tile.direction = (1, 0)
                elif self.get_tile(game_state, (x - self.tile_width, y)).is_walkable:
                    tile.direction = (-1, 0)
                elif self.get_tile(game_state, (x, y + self.tile_height)).is_walkable:
                    tile.direction = (0, 1)
                elif self.get_tile(game_state, (x, y - self.tile_height)).is_walkable:
                    tile.direction = (0, -1)
                else:
                    tile.direction = (1, 0)
