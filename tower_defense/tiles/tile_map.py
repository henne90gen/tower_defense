import copy
import os
import pickle
from typing import Dict, Tuple

import pyglet

from ..game_types import TileType
from ..graphics import Renderer
from ..helper import Vector, rect_contains_point, process_clicks, MouseClick
from .tile import Tile


class TileMap:
    def __init__(self):
        self.path = ""
        self.border_width = 50
        self.tile_size = Vector(100, 100)
        self.max_tiles = Vector(10, 10)
        self.tiles: Dict[(int, int), Tile] = self.generate_tiles(
            self.max_tiles, self.tile_size)

    @staticmethod
    def generate_tiles(max_tiles: Vector, tile_size: Vector) -> dict:
        tiles = {}
        for x in range(int(max_tiles.x)):
            for y in range(int(max_tiles.y)):
                tile = Tile(Vector(x, y), tile_size, TileType.BUILDING_GROUND)
                tiles[(x, y)] = tile
        return tiles

    def new(self, game_state, path: str, size: Vector):
        game_state.entity_manager.reset()
        self.path = path.strip()
        self.max_tiles = size.copy()
        self.tiles = self.generate_tiles(self.max_tiles, self.tile_size)
        self.save()

    def load(self, game_state, path: str):
        game_state.entity_manager.reset()
        self.path = path.strip()
        if os.path.isfile(self.path):
            with open(self.path, "rb") as f:
                self.tiles, self.max_tiles = pickle.load(f)
                print("Loaded tile map", self.path)

            # update tile size to current tile size
            for tile in self.tiles:
                self.tiles[tile].size = self.tile_size

    def save(self):
        if self.path:
            with open(self.path, "wb") as f:
                pickle.dump((self.tiles, self.max_tiles), f)
                print("Saved tile map", self.path)

    @property
    def tile_map_width(self):
        return self.tile_size.x * self.max_tiles.x

    @property
    def tile_map_height(self):
        return self.tile_size.y * self.max_tiles.y

    @property
    def has_start_node(self):
        for tile in self.tiles:
            if self.tiles[tile].tile_type == TileType.START:
                return True
        return False

    @property
    def has_finish_node(self):
        for tile in self.tiles:
            if self.tiles[tile].tile_type == TileType.FINISH:
                return True
        return False

    def is_on_map(self, position: Vector):
        return 0 < position.x < self.tile_map_width and 0 < position.y < self.tile_map_height

    def render(self, game_state):
        batch = pyglet.graphics.Batch()

        size = Vector(self.tile_map_width + self.border_width * 2,
                      self.tile_map_height + self.border_width * 2)
        position = game_state.world_offset - \
            Vector(self.border_width, self.border_width)
        Renderer.rectangle_border(batch, position, size, (255, 255, 255),
                                  border_width=self.border_width)

        for tile in self.tiles.values():
            tile.render(game_state, batch)

        batch.draw()

    def update(self, game_state):
        process_clicks(game_state, self.mouse_click_handler)

    def mouse_click_handler(self, _, click: MouseClick) -> bool:
        return False

    def path_finding(self):
        for tile in self.tiles:
            self.tiles[tile].directions = []

        graph = self.get_tile_graph()
        paths = {}
        for node in graph:
            paths[node] = {}
            paths[node]['open_directions'] = graph[node]
            paths[node]['to_path'] = []
            paths[node]['from_path'] = []

        starting_node = None
        finish_node = None
        for tile in self.tiles:
            if self.tiles[tile].tile_type == TileType.START:
                starting_node = tile
            elif self.tiles[tile].tile_type == TileType.FINISH:
                finish_node = tile
        if starting_node is None:
            return
        if finish_node is None:
            return

        paths[starting_node]['to_path'] = [starting_node]
        paths[finish_node]['open_directions'] = []

        while True:
            start_node = self.select_start_node(paths)
            if start_node is None:
                # no start nodes left
                break

            path = [start_node]
            # create working copy of paths
            temp_paths = copy.deepcopy(paths)
            current_node = start_node
            while True:
                open_directions = temp_paths[current_node]['open_directions']
                if open_directions:
                    # there are possible directions to go in

                    direction = open_directions[0]
                    next_node = direction[0]
                    path.append(next_node)

                    # remove the links between current_node and next_node
                    temp_paths[current_node]['open_directions'] = self.remove_node_from_open_directions(
                        next_node,
                        open_directions
                    )
                    next_open_directions = temp_paths[next_node]['open_directions']
                    temp_paths[next_node]['open_directions'] = self.remove_node_from_open_directions(
                        current_node,
                        next_open_directions
                    )

                    current_node = next_node
                elif current_node == finish_node:
                    # path has successfully terminated
                    break
                elif paths[current_node]['to_path']:
                    # path has met up with a path that is known to terminate successfully
                    break
                elif current_node == start_node:
                    # we are back at the start and don't have any directions left to go
                    path = None
                    break
                else:
                    # go back to last intersection with directions not yet processed
                    while not temp_paths[current_node]['open_directions']:
                        if current_node == start_node:
                            path = None
                            break
                        path = path[:-1]
                        current_node = path[-1]

            if path is None:
                # we can't go anywhere from start_node
                paths[start_node]['open_directions'] = []
                continue

            # updating paths with newly discovered path
            rest_path = path
            for index, node in enumerate(path):
                paths[node]['to_path'] = path[:index + 1]
                if rest_path not in paths[node]['from_path']:
                    paths[node]['from_path'].append(rest_path)

                if rest_path:
                    rest_path = rest_path[1:]

                if index > 0:
                    # remove the links between node and previous_node
                    previous_node = path[index - 1]
                    paths[node]['open_directions'] = self.remove_node_from_open_directions(previous_node, paths[node][
                        'open_directions'])
                    paths[previous_node]['open_directions'] = self.remove_node_from_open_directions(node, paths[
                        previous_node]['open_directions'])
                else:
                    # remove the links between node and start_node
                    paths[node]['open_directions'] = self.remove_node_from_open_directions(start_node, paths[node][
                        'open_directions'])
                    paths[start_node]['open_directions'] = self.remove_node_from_open_directions(node,
                                                                                                 paths[start_node][
                                                                                                     'open_directions'])

        # updating directions in tile map
        for node in paths:
            directions = []
            for p in paths[node]['from_path']:
                if len(p) > 1:
                    d = p[1][0] - p[0][0], p[1][1] - p[0][1]
                    directions.append(d)
            self.tiles[node].directions = directions

    @staticmethod
    def remove_node_from_open_directions(node: Tuple[int, int], open_directions: list):
        for n in open_directions.copy():
            if n[0] == node:
                open_directions.remove(n)
        return open_directions

    @staticmethod
    def select_start_node(paths):
        for node in paths:
            if paths[node]['to_path'] and paths[node]['open_directions']:
                return node
        return None

    def get_tile_graph(self) -> dict:
        graph: dict = {}
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

        return graph


class EditorTileMap(TileMap):
    def render(self, game_state):
        super().render(game_state)

        arrow_batch = pyglet.graphics.Batch()
        for tile in self.tiles.values():
            tile.render_arrow(game_state, arrow_batch)
        arrow_batch.draw()

    def mouse_click_handler(self, _, click: MouseClick) -> bool:
        if not self.is_on_map(click.position) or click.button != 1:
            return False

        for tile in self.tiles.values():
            if rect_contains_point(click.position, Vector(tile.world_position.x, tile.world_position.y + tile.size.y),
                                   tile.size):
                allow_start = True
                allow_finish = True
                for key in self.tiles:
                    if self.tiles[key].tile_type == TileType.START:
                        allow_start = False
                    elif self.tiles[key].tile_type == TileType.FINISH:
                        allow_finish = False

                tile.next_type(allow_start, allow_finish)

                self.path_finding()

                return True

        return False


class GameTileMap(TileMap):
    def __init__(self):
        super().__init__()
        self.path_finding()
        self.highlighted_tile = None

    def render(self, game_state):
        super().render(game_state)

        highlight_batch = pyglet.graphics.Batch()
        for tile in self.tiles.values():
            if tile.highlighted:
                tile.render_highlight(game_state, highlight_batch)
                break
        highlight_batch.draw()

    def mouse_click_handler(self, game_state, click: MouseClick) -> bool:
        if not self.is_on_map(click.position) or click.button != 1:
            return False

        for tile in self.tiles:
            if rect_contains_point(click.position, Vector(self.tiles[tile].world_position.x,
                                                          self.tiles[tile].world_position.y + self.tiles[tile].size.y),
                                   self.tiles[tile].size):
                if self.tiles[tile].tile_type == TileType.BUILDING_GROUND:
                    self.tiles[tile].highlighted = not self.tiles[tile].highlighted
                    if self.tiles[tile].highlighted:
                        self.highlighted_tile = tile
                    else:
                        self.highlighted_tile = None
                else:
                    self.highlighted_tile = None

                for other_tile in self.tiles:
                    if tile == other_tile:
                        continue
                    self.tiles[other_tile].highlighted = False
                return True
        return False
