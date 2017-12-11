import pyglet

from game_types import TileType
from graphics import render_textured_rectangle, render_colored_rectangle
from helper import Vector


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
        # noinspection PyTypeChecker
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

        if self.tile_type == TileType.START or self.tile_type == TileType.FINISH:
            if self.tile_type == TileType.START:
                color = (0, 255, 0)
            else:
                color = (255, 0, 0)
            render_colored_rectangle(batch, color, Vector(x, y), self.size)
        else:
            render_textured_rectangle(batch, game_state.textures.tiles[self.tile_type], Vector(x, y), self.size,
                                      tex_max=0.75)

        if len(self.directions) == 0:
            return
        if self.direction_index >= len(self.directions):
            self.direction_index = 0

        dir_x, dir_y = self.directions[self.direction_index % len(self.directions)]
        self.timer += 1
        if self.timer > 50:
            self.timer = 0
            self.direction_index = self.direction_index + 1

        tex_max = 0.8
        tex_top_left = Vector(0, tex_max)
        tex_top_right = Vector(tex_max, tex_max)
        tex_bottom_left = Vector()
        tex_bottom_right = Vector(tex_max, 0)

        if dir_x < 0:
            # flip horizontally
            tex_top_left = Vector(tex_max, tex_max)
            tex_top_right = Vector(0, tex_max)
            tex_bottom_left = Vector(tex_max, 0)
            tex_bottom_right = Vector()
        elif dir_y < 0:
            # rotate down
            tex_top_left = Vector()
            tex_top_right = Vector(0, tex_max)
            tex_bottom_left = Vector(tex_max, 0)
            tex_bottom_right = Vector(tex_max, tex_max)
        elif dir_y > 0:
            # rotate up
            tex_top_left = Vector(tex_max, tex_max)
            tex_top_right = Vector(tex_max, 0)
            tex_bottom_left = Vector(0, tex_max)
            tex_bottom_right = Vector()

        texture_coords = [tex_bottom_right.x, tex_bottom_right.y,
                          tex_top_right.x, tex_top_right.y,
                          tex_top_left.x, tex_top_left.y,
                          tex_bottom_left.x, tex_bottom_left.y]
        render_textured_rectangle(arrow_batch, game_state.textures.other['arrow'], Vector(x, y), self.size,
                                  texture_coords=texture_coords)
