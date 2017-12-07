import os
import pickle
from queue import LifoQueue, Queue
from typing import Dict
import copy

import pyglet

from game_types import TileType
from helper import Vector, rect_contains_point


class Tile:
    def __init__(self, position: Vector, size: Vector, tile_type: TileType):
        self.position = position
        self.size = size
        self.tile_type = tile_type
        self.directions = []
        self.direction_index = 0
        self.timer = 0

    def __eq__(self, other):
        if type(other) != Tile:
            return False
        return self.position == other.position and self.size == other.size and self.tile_type == other.tile_type

    def __str__(self):
        return "Tile: " + str(self.position) + ":" + str(self.size) + " - " + str(self.tile_type)

    @property
    def is_walkable(self):
        return self.tile_type != TileType.BUILDING_GROUND

    @property
    def world_position(self):
        return Vector(self.position.x * self.size.x, self.position.y * self.size.y)

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

    def render_label(self, game_state, batch: pyglet.graphics.Batch):
        x = self.position.x * self.size.x + game_state.world_offset.x
        y = self.position.y * self.size.y + game_state.world_offset.y

        if x + self.size.x < 0 or y + self.size.y < 0:
            return
        if x > game_state.window_size.x or y - self.size.y > game_state.window_size.y:
            return
        pyglet.text.Label(str(self.position) + " " + str(self.world_position),
                          font_name='DejaVuSans',
                          font_size=10,
                          color=(255, 0, 0, 255),
                          batch=batch, x=x, y=y,
                          anchor_x='left', anchor_y='bottom')

    def render(self, game_state, batch: pyglet.graphics.Batch, arrow_batch: pyglet.graphics.Batch):
        x = self.position.x * self.size.x + game_state.world_offset.x
        y = self.position.y * self.size.y + game_state.world_offset.y
        if x + self.size.x < 0 or y + self.size.y < 0:
            return
        if x > game_state.window_size.x or y - self.size.y > game_state.window_size.y:
            return

        top_left = Vector(x, y + self.size.y)
        bottom_right = Vector(top_left.x + self.size.x, top_left.y - self.size.y)
        vertices = [bottom_right.x, bottom_right.y,
                    bottom_right.x, top_left.y,
                    top_left.x, top_left.y,
                    top_left.x, bottom_right.y]

        if self.tile_type == TileType.START or self.tile_type == TileType.FINISH:
            if self.tile_type == TileType.START:
                color = (0, 255, 0)
            else:
                color = (255, 0, 0)
            batch.add(4, pyglet.graphics.GL_QUADS, None, ('v2f', vertices), ('c3B', (*color, *color, *color, *color)))
        else:
            texture_coords = [0.75, 0.0,
                              0.75, 0.75,
                              0.0, 0.75,
                              0.0, 0.0]
            batch.add(4, pyglet.graphics.GL_QUADS, game_state.textures.tiles[self.tile_type], ('v2f/static', vertices),
                      ('t2f/static', texture_coords))

        if len(self.directions) == 0:
            return
        if self.direction_index >= len(self.directions):
            self.direction_index = 0

        dir_x, dir_y = self.directions[self.direction_index % len(self.directions)]
        self.timer += 1
        if self.timer > 50:
            self.timer = 0
            self.direction_index = self.direction_index + 1

        tex_top_left = Vector(0, 0.75)
        tex_top_right = Vector(0.75, 0.75)
        tex_bottom_left = Vector()
        tex_bottom_right = Vector(0.75, 0)

        if dir_x < 0:
            # flip horizontally
            tex_top_left = Vector(0.75, 0.75)
            tex_top_right = Vector(0, 0.75)
            tex_bottom_left = Vector(0.75, 0)
            tex_bottom_right = Vector()
        elif dir_y < 0:
            # rotate down
            tex_top_left = Vector()
            tex_top_right = Vector(0, 0.75)
            tex_bottom_left = Vector(0.75, 0)
            tex_bottom_right = Vector(0.75, 0.75)
        elif dir_y > 0:
            # rotate up
            tex_top_left = Vector(0.75, 0.75)
            tex_top_right = Vector(0.75, 0)
            tex_bottom_left = Vector(0, 0.75)
            tex_bottom_right = Vector()

        texture_coords = [tex_bottom_right.x, tex_bottom_right.y,
                          tex_top_right.x, tex_top_right.y,
                          tex_top_left.x, tex_top_left.y,
                          tex_bottom_left.x, tex_bottom_left.y]
        arrow_batch.add(4, pyglet.graphics.GL_QUADS, game_state.textures.other['arrow'], ('v2f/static', vertices),
                        ('t2f/static', texture_coords))


class TileMap:
    def __init__(self):
        self.path = ""
        self.border_width = 50
        self.cursor_position = Vector()
        self.tile_width = 100
        self.tile_height = 100
        self.max_tiles = Vector(10, 10)
        self.tiles: Dict[(int, int), Tile] = {}
        self.generate_tiles()

    def generate_tiles(self):
        self.tiles = {}
        for x in range(self.max_tiles.x):
            for y in range(self.max_tiles.y):
                tile = Tile(Vector(x, y), Vector(self.tile_width, self.tile_height), TileType.BUILDING_GROUND)
                self.tiles[(x, y)] = tile

    def new(self, path: str, width: int, height: int):
        self.path = path.strip()
        self.max_tiles.x = width
        self.max_tiles.y = height
        self.generate_tiles()
        self.save()

    def load(self, path: str):
        self.path = path.strip()
        if os.path.isfile(self.path):
            with open(self.path, "rb") as f:
                self.tiles, self.max_tiles = pickle.load(f)
                print("Loaded tile map", self.path)

    def save(self):
        if len(self.path) > 0:
            with open(self.path, "wb") as f:
                pickle.dump((self.tiles, self.max_tiles), f)
                print("Saved tile map", self.path)

    def render_border(self, game_state):
        def draw_rect(p1, p2, color):
            vertices = [p1.x, p1.y, p2.x, p1.y, p2.x, p2.y, p1.x,
                        p2.y]
            pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f', vertices), ('c3B', (*color, *color, *color, *color)))

        top_left = Vector(-self.border_width, 0) + game_state.world_offset
        bottom_right = top_left + Vector(self.tile_map_width + self.border_width, -self.border_width)
        draw_rect(top_left, bottom_right, (0, 255, 255))

        top_left = Vector(0, 0) + game_state.world_offset
        bottom_right = top_left + Vector(-self.border_width, self.tile_map_height + self.border_width)
        draw_rect(top_left, bottom_right, (255, 0, 255))

        top_left = Vector(0, self.tile_map_height) + game_state.world_offset
        bottom_right = top_left + Vector(self.tile_map_width + self.border_width, self.border_width)
        draw_rect(top_left, bottom_right, (255, 255, 0))

        top_left = Vector(self.tile_map_width, -self.border_width) + game_state.world_offset
        bottom_right = top_left + Vector(self.border_width, self.tile_map_height + self.border_width)
        draw_rect(top_left, bottom_right, (255, 0, 0))

    @property
    def tile_map_width(self):
        return self.tile_width * self.max_tiles.x

    @property
    def tile_map_height(self):
        return self.tile_height * self.max_tiles.y

    def is_on_map(self, game_state, position: (int, int), pos_is_in_tile_map_space: bool = True):
        if not pos_is_in_tile_map_space:
            position = game_state.to_tile_map_space(position)
        x, y = position.x, position.y
        return 0 < x < self.tile_map_width and 0 < y < self.tile_map_height

    def get_tile_index(self, position: Vector) -> (int, int):
        return int(position.x / self.tile_width), int(position.y / self.tile_height)

    def render(self, game_state):
        self.render_border(game_state)

        batch = pyglet.graphics.Batch()
        arrow_batch = pyglet.graphics.Batch()
        for tile in self.tiles.values():
            tile.render(game_state, batch, arrow_batch)
        batch.draw()
        arrow_batch.draw()

    def update(self, game_state):
        self.cursor_position = game_state.to_tile_map_space(game_state.mouse_position)

        if not game_state.editor_mode:
            return

        for click in game_state.mouse_clicks.copy():
            pos = game_state.to_tile_map_space(click.position)
            print(pos)
            if not self.is_on_map(game_state, pos):
                print("click is not on map")
                continue

            for tile in self.tiles.values():
                if rect_contains_point(pos, Vector(tile.world_position.x, tile.world_position.y + tile.size.y),
                                       tile.size):
                    allow_start = True
                    allow_finish = True
                    for key in self.tiles:
                        if self.tiles[key].tile_type == TileType.START:
                            allow_start = False
                        elif self.tiles[key].tile_type == TileType.FINISH:
                            allow_finish = False
                    tile.next_type(allow_start, allow_finish)

        for tile in self.tiles:
            self.tiles[tile].directions = []

        # self.breadth_first_search()
        self.path_finding()

    def path_finding(self):
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
            return None
        if finish_node is None:
            return None

        paths[starting_node]['to_path'] = [starting_node]
        paths[finish_node]['open_directions'] = []

        while True:
            start_node = self.get_next_node(paths)
            if start_node is None:
                break

            path = [start_node]
            temp_paths = copy.deepcopy(paths)
            current_node = start_node
            while True:
                open_directions = temp_paths[current_node]['open_directions']
                if len(open_directions) > 0:
                    direction = open_directions[0]

                    next_node = direction[0]
                    path.append(next_node)

                    temp_paths[current_node]['open_directions'] = self.remove_node_from_open_directions(next_node,
                                                                                                        open_directions)
                    next_open_directions = temp_paths[next_node]['open_directions']
                    temp_paths[next_node]['open_directions'] = self.remove_node_from_open_directions(current_node,
                                                                                                     next_open_directions)
                    current_node = next_node
                elif current_node == finish_node:
                    # path has successfully terminated
                    break
                elif len(paths[current_node]['to_path']) > 0:
                    # path has met up with a path that is known to terminate successfully
                    break
                elif current_node == start_node:
                    path = None
                    break
                else:
                    # go back to last valid
                    while len(temp_paths[current_node]['open_directions']) == 0:
                        if current_node == start_node:
                            path = None
                            break
                        path = path[:-1]
                        current_node = path[-1]

            if path is None:
                paths[start_node]['open_directions'] = []
                continue

            # start_path = paths[start_node]['to_path']
            rest_path = path
            for index, node in enumerate(path):
                paths[node]['to_path'] = path[:index + 1]
                if rest_path not in paths[node]['from_path']:
                    paths[node]['from_path'].append(rest_path)

                if len(rest_path) > 0:
                    rest_path = rest_path[1:]

                if index > 0:
                    paths[node]['open_directions'] = self.remove_node_from_open_directions(path[index - 1], paths[node][
                        'open_directions'])
                    paths[path[index - 1]]['open_directions'] = self.remove_node_from_open_directions(node, paths[
                        path[index - 1]]['open_directions'])
                else:
                    paths[node]['open_directions'] = self.remove_node_from_open_directions(start_node, paths[node][
                        'open_directions'])
                    paths[start_node]['open_directions'] = self.remove_node_from_open_directions(node,
                                                                                                 paths[start_node][
                                                                                                     'open_directions'])

        for node in paths:
            directions = []
            for p in paths[node]['from_path']:
                if len(p) > 1:
                    d = p[1][0] - p[0][0], p[1][1] - p[0][1]
                    directions.append(d)
            self.tiles[node].directions = directions

    @staticmethod
    def remove_node_from_open_directions(node: (int, int), open_directions: list):
        for n in open_directions.copy():
            if n[0] == node:
                open_directions.remove(n)
        return open_directions

    @staticmethod
    def get_next_node(paths):
        for node in paths:
            if len(paths[node]['to_path']) > 0 and len(paths[node]['open_directions']) > 0:
                return node
        return None

    def _path_finding(self):
        graph = self.get_tile_graph()
        paths = []

        not_included_nodes = list(graph.keys())

        while len(not_included_nodes) > 0:
            path = self.find_path_to_finish(graph, paths)

            if path is None:
                return

            if path not in paths:
                paths.append(path)
            else:
                break

            for node in path:
                if node in not_included_nodes:
                    not_included_nodes.remove(node)

        for path in paths:
            for index, node in enumerate(path):
                if index > 0:
                    previous_node = path[index - 1]
                    tile = self.tiles[previous_node]
                    direction = node[0] - previous_node[0], node[1] - previous_node[1]
                    tile.directions.append(direction)

    def find_path_to_finish(self, graph, paths):
        # find start node and finish node
        starting_node = None
        finish_node = None
        for tile in self.tiles:
            if self.tiles[tile].tile_type == TileType.START:
                starting_node = tile
            elif self.tiles[tile].tile_type == TileType.FINISH:
                finish_node = tile
        if starting_node is None:
            return None
        if finish_node is None:
            return None

        path = [starting_node]
        intersection_options = {}  # key: node, value: [routes not taken yet]
        current_node = starting_node

        # initialize options dictionary with current node
        intersection_options[current_node] = []
        for direction in graph[current_node]:
            intersection_options[current_node].append(direction)

        while True:
            if current_node in intersection_options:
                options = intersection_options[current_node]
            else:
                possible_directions = graph[current_node]
                options = []
                for direction in possible_directions:
                    if direction[0] in path:
                        continue
                    options.append(direction)

            if len(options) == 0 and len(intersection_options.keys()) == 0:
                # no more options left
                # print("Didn't find one!")
                return path

            if current_node == finish_node and path not in paths:
                # path to finish has been found
                print("Found one!")
                return path
            elif len(options) > 0:
                option = options[0]
                options = options[1:]
                for opt in options.copy():
                    if opt[0] in path:
                        options.remove(opt)
                if len(options) == 0:
                    if current_node in intersection_options:
                        del intersection_options[current_node]
                else:
                    intersection_options[current_node] = options
                current_node = option[0]
                path.append(current_node)
            else:
                if current_node in intersection_options:
                    del intersection_options[current_node]
                for index, node in enumerate(path[::-1]):
                    if node in intersection_options and len(intersection_options[node]) > 0:
                        current_node = node
                        break
                path = path[:path.index(current_node) + 1]

    def breadth_first_search(self):
        graph = self.get_tile_graph()

        not_visited_nodes = list(graph.keys())
        next_nodes = Queue()
        starting_node = None
        finish_node = None

        for tile in self.tiles:
            if self.tiles[tile].tile_type == TileType.START:
                starting_node = tile
            elif self.tiles[tile].tile_type == TileType.FINISH:
                finish_node = tile

        while len(not_visited_nodes) > 0:
            if starting_node:
                current_node = starting_node
                starting_node = None
            else:
                current_node = not_visited_nodes[0]

            not_visited_nodes.remove(current_node)

            for node in graph[current_node]:
                if node[0] in not_visited_nodes:
                    next_nodes.put(node)

            while not next_nodes.empty():
                next_node = next_nodes.get()

                if self.tiles[next_node[0]].tile_type == TileType.FINISH:
                    continue

                if next_node[0] in not_visited_nodes:
                    not_visited_nodes.remove(next_node[0])

                previous_node = None
                for node in graph[next_node[0]]:
                    if node[0] not in not_visited_nodes:
                        previous_node = node[0]

                if previous_node:
                    direction = None
                    for node in graph[previous_node]:
                        if node[0] == next_node[0]:
                            direction = node[1]
                    if direction and direction not in self.tiles[previous_node].directions:
                        self.tiles[previous_node].directions.append(direction)

                for node in graph[next_node[0]]:
                    if node[0] in not_visited_nodes:
                        next_nodes.put(node)

        if not finish_node:
            return

        for node in graph[finish_node]:
            direction = None
            for _node in graph[node[0]]:
                if _node[0] == finish_node:
                    direction = _node[1]
            if direction and direction not in self.tiles[node[0]].directions:
                self.tiles[node[0]].directions.append(direction)

    def depth_first_search(self):
        graph = self.get_tile_graph()

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
                not_visited_nodes.remove(tile)
                graph[tile] = []

        # TODO make it prefer straight lines over bends
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
                    # next node is adjacent to current node
                    if next_node[1] not in self.tiles[current_node].directions:
                        self.tiles[current_node].directions.append(next_node[1])
                elif self.tiles[current_node].tile_type != TileType.FINISH:
                    # TODO find the correct direction before reaching the finish
                    # self.tiles[current_node].direction = self.tiles[last_node].direction
                    pass

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

        # TODO maybe re-enable this
        # if len(graph[current_node]) > 0 and self.tiles[graph[current_node][0][0]].direction != (0, 0):
        #     self.tiles[current_node].direction = self.tiles[last_node].direction

    def get_tile_graph(self) -> dict:
        graph = {}
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
