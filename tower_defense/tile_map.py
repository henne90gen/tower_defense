import os
import pickle
from queue import LifoQueue, Queue
from typing import Dict

import pygame

from game_types import TileType


class Tile:
    def __init__(self, rect: pygame.Rect, tile_type: TileType):
        self.rect: pygame.Rect = rect
        self.tile_type = tile_type
        self.direction = None

    def __eq__(self, other):
        if type(other) != Tile:
            return False
        return self.rect == other.rect and self.tile_type == other.tile_type

    def __str__(self):
        return "Tile: " + str(self.rect) + " - " + str(self.tile_type)

    @property
    def is_walkable(self):
        return self.tile_type != TileType.BUILDING_GROUND

    def next_type(self, allow_start: bool, allow_finish: bool):
        type_list = list(TileType)
        index = type_list.index(self.tile_type)
        index += 1

        if index >= len(type_list):
            index = 0

        self.tile_type = type_list[index]
        if (not allow_start and self.tile_type == TileType.START) or \
                (not allow_finish and self.tile_type == TileType.FINISH):
            self.next_type(allow_start, allow_finish)

        return True

    def render(self, game_state, screen: pygame.Surface):
        x = self.rect.left + game_state.world_offset_x
        y = self.rect.top + game_state.world_offset_y
        area = pygame.Rect(0, 0, self.rect.width, self.rect.height)
        if self.tile_type == TileType.START:
            screen.fill((0, 255, 0), pygame.Rect((x, y), (self.rect.width, self.rect.height)))
        elif self.tile_type == TileType.FINISH:
            screen.fill((255, 0, 0), pygame.Rect((x, y), (self.rect.width, self.rect.height)))
        else:
            screen.blit(game_state.textures.tiles[self.tile_type], (x, y), area)

        arrow = game_state.textures.other['arrow']
        arrow = pygame.transform.scale(arrow, (self.rect.width, self.rect.height))

        if not self.direction:
            return

        dir_x, dir_y = self.direction

        if dir_x < 0:
            arrow = pygame.transform.flip(arrow, True, False)
        elif dir_y < 0:
            arrow = pygame.transform.rotate(arrow, 90)
        elif dir_y > 0:
            arrow = pygame.transform.rotate(arrow, -90)

        screen.blit(arrow, (x, y), area)


class TileMap:
    def __init__(self):
        self.path = ""
        self.border_width = 50
        self.cursor_position = (0, 0)
        self.tile_width = 100
        self.tile_height = 100
        self.max_tiles_x = 10
        self.max_tiles_y = 10
        self.tiles: Dict[(int, int), Tile] = {}
        self.generate_tiles()

    def generate_tiles(self):
        self.tiles = {}
        for x in range(self.max_tiles_x):
            for y in range(self.max_tiles_y):
                tile = Tile(
                    pygame.Rect((x * self.tile_width, y * self.tile_height), (self.tile_width, self.tile_height)),
                    TileType.BUILDING_GROUND)
                self.tiles[(x, y)] = tile

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

        for tile in self.tiles.values():
            if tile.rect.contains(pygame.Rect(position, (0, 0))):
                return tile

    def render(self, game_state, screen: pygame.Surface):
        self.render_border(game_state, screen)

        for tile in self.tiles.values():
            tile.render(game_state, screen)

    def update(self, game_state):
        self.cursor_position = game_state.to_world_space(game_state.mouse_position)

        if not game_state.editor_mode:
            return

        for click in game_state.mouse_clicks.copy():
            pos = game_state.to_world_space(click.pos)
            if not self.is_on_map(game_state, pos, True):
                continue

            for tile in self.tiles.values():
                if tile.rect.contains(pygame.Rect(pos, (0, 0))):
                    allow_start = True
                    allow_finish = True
                    for key in self.tiles:
                        if self.tiles[key].tile_type == TileType.START:
                            allow_start = False
                        elif self.tiles[key].tile_type == TileType.FINISH:
                            allow_finish = False
                    tile.next_type(allow_start, allow_finish)

        for tile in self.tiles:
            self.tiles[tile].direction = None

        graph = {}

        # setting up graph
        for position in self.tiles:
            if self.tiles[position].is_walkable:
                graph[position] = []

                x, y = position
                left_pos = (x - 1, y)
                right_pos = (x + 1, y)
                top_pos = (x, y - 1)
                bottom_pos = (x, y + 1)

                if top_pos in self.tiles and self.tiles[top_pos].is_walkable:
                    graph[position].append((top_pos, (0, -1)))

                if right_pos in self.tiles and self.tiles[right_pos].is_walkable:
                    graph[position].append((right_pos, (1, 0)))

                if bottom_pos in self.tiles and self.tiles[bottom_pos].is_walkable:
                    graph[position].append((bottom_pos, (0, 1)))

                if left_pos in self.tiles and self.tiles[left_pos].is_walkable:
                    graph[position].append((left_pos, (-1, 0)))

        # searching graph for paths
        not_visited_nodes = list(graph.keys())
        visited_nodes = []
        next_nodes = LifoQueue()
        current_node = None
        last_node = None
        starting_node = None
        for tile in self.tiles:
            if self.tiles[tile].tile_type == TileType.START:
                starting_node = tile
            elif self.tiles[tile].tile_type == TileType.FINISH:
                # not_visited_nodes.remove(tile)
                graph[tile] = []

        while len(not_visited_nodes) > 0:
            if starting_node:
                current_node = starting_node
                starting_node = None
            else:
                current_node = not_visited_nodes[0]
            not_visited_nodes.remove(current_node)
            visited_nodes.append(current_node)

            for node in graph[current_node]:
                if node[0] not in visited_nodes:
                    next_nodes.put(node)

            while not next_nodes.empty():
                next_node = next_nodes.get()

                if next_node in graph[current_node]:
                    self.tiles[current_node].direction = next_node[1]
                else:
                    self.tiles[current_node].direction = self.tiles[last_node].direction

                last_node = current_node
                current_node = next_node[0]
                if current_node in not_visited_nodes:
                    not_visited_nodes.remove(current_node)
                visited_nodes.append(current_node)

                if self.tiles[current_node].tile_type == TileType.FINISH:
                    continue

                for node in graph[current_node]:
                    if node[0] not in visited_nodes:
                        next_nodes.put(node)

                        # if len(graph[current_node]) > 0 and self.tiles[graph[current_node][0][0]].direction != (0, 0):
                        #     self.tiles[current_node].direction = graph[current_node][0][1]
