import os
from typing import List

import pyglet

from game_types import BuildingType
from graphics import Renderer
from helper import Vector, MouseClick, process_clicks, rect_contains_point
from user_interface.components import TextComponent, Input, HighlightComponent

MAPS_PATH = './res/maps/'


class Dialog:
    def __init__(self, visible: bool):
        self.position = Vector()
        self.visible = visible

    def open(self, game_state):
        self.visible = True
        self.position.y = game_state.window_size.y - 200

    def close(self):
        self.visible = False

    def render(self):
        pass

    def update(self, game_state):
        game_state.key_presses.up = game_state.key_presses.down = game_state.key_presses.left = game_state.key_presses.right = False


class NewMapDialog(Dialog):
    def __init__(self, visible: bool = False):
        super().__init__(visible)
        self.position = Vector(200, 0)
        text_width = 150
        text_height = 40

        self.components = {
            'width_text': TextComponent("Width:", Vector(0, 0), Vector(text_width, text_height)),
            'width_input': Input(Vector(text_width, 0), Vector(300, text_height), has_focus=True),

            'height_text': TextComponent("Height:",
                                         Vector(0, -text_height), Vector(text_width, text_height)),
            'height_input': Input(Vector(text_width, -text_height), Vector(300, text_height)),

            'name_text': TextComponent("Name:",
                                       Vector(0, -text_height * 2), Vector(text_width, text_height)),
            'name_input': Input(Vector(text_width, -text_height * 2), Vector(300, text_height)),

            'submit_button': TextComponent("Create",
                                           Vector(0, -text_height * 3), Vector(text_width, text_height)),
            'cancel_button': TextComponent("Cancel", Vector(text_width, -text_height * 3),
                                           Vector(text_width, text_height))
        }

        self.handlers = {
            'width_input': None,
            'height_input': None,
            'name_input': None,
            'submit_button': self.submit_func,
            'cancel_button': self.cancel_func
        }

    def open(self, game_state):
        super().open(game_state)
        self.components['width_input'].update(text="")
        self.components['height_input'].update(text="")
        self.components['name_input'].update(text="")

    def render(self):
        if self.visible:
            for component in self.components:
                self.components[component].render(self.position)

    def submit_func(self, game_state):
        try:
            new_width = int(self.components['width_input'].text)
            new_height = int(self.components['height_input'].text)
        except Exception as e:
            print(e)
            return
        if self.components['name_input'].text:
            game_state.tile_map.new(game_state, MAPS_PATH + self.components['name_input'].text + '.map',
                                    Vector(new_width, new_height))
        self.visible = False

    def cancel_func(self, _):
        self.visible = False

    def update(self, game_state):
        super().update(game_state)

        for component in self.components:
            if 'input' in component:
                self.components[component].add_text(game_state.key_presses)

        process_clicks(game_state, self.mouse_click_handler, False, self.position)

    def mouse_click_handler(self, game_state, click: MouseClick) -> bool:
        for component in self.components:
            if component in self.handlers:
                if self.components[component].is_clicked(click):
                    if 'input' in component:
                        self.give_exclusive_focus(component)
                    else:
                        self.handlers[component](game_state)
                    return True
        return False

    def give_exclusive_focus(self, component: str):
        for other_component in self.components:
            if component == other_component and 'input' in component:
                continue
            if 'input' in other_component:
                self.components[other_component].has_focus = False


class LoadMapDialog(Dialog):
    def __init__(self, visible: bool = False):
        super().__init__(visible)
        self.maps: List[TextComponent] = []
        self.cancel_button: TextComponent = None

    def refresh_maps(self, maps_path: str):
        self.maps = []
        current_index = 0
        height = 50
        for file in os.listdir(maps_path):
            if '.map' in file:
                text_component = TextComponent(file, Vector(150, 100 - height * current_index), Vector(300, height))
                self.maps.append(text_component)
                current_index += 1
        return current_index, height

    def update_cancel_button(self, current_index, height):
        self.cancel_button = TextComponent("Cancel", Vector(150, 100 - height * current_index), Vector(200, height))

    def open(self, game_state):
        super().open(game_state)
        current_index, height = self.refresh_maps(MAPS_PATH)
        self.update_cancel_button(current_index, height)

    def update(self, game_state):
        super().update(game_state)
        process_clicks(game_state, self.mouse_click_handler, False, self.position)

    def mouse_click_handler(self, game_state, click):
        if self.cancel_button.is_clicked(click):
            self.visible = False
            return True
        for tile_map in self.maps:
            if tile_map.is_clicked(click):
                game_state.tile_map.load(game_state, MAPS_PATH + tile_map.text)
                self.visible = False
                return True
        return False

    def render(self):
        if self.visible:
            for tile_map in self.maps:
                tile_map.render(self.position)
            self.cancel_button.render(self.position)


class BuildingDialog(Dialog):
    def __init__(self):
        super().__init__(False)
        self.background_size = Vector(200, 0)
        self.button_size = Vector(200, 50)
        self.components = {
            'build_button': TextComponent("Build", Vector(0, self.button_size.y), self.button_size),
            'upgrade_button': TextComponent("Upgrade", Vector(0, self.button_size.y), self.button_size, visible=False)
        }
        self.handlers = {
            'build_button': self.build_func,
            'upgrade_button': self.upgrade_func
        }
        self.building_types = {
            BuildingType.LASER: HighlightComponent("", Vector(), Vector()),
            BuildingType.CATAPULT: HighlightComponent("", Vector(), Vector()),
        }
        # self.upgrade_buttons = {}

    def open(self, game_state):
        super().open(game_state)
        self.position = Vector()

        position = Vector(0, game_state.window_size.y)
        # noinspection PyTypeChecker
        for index, bt in enumerate(BuildingType):
            highlight = index == 0
            self.building_types[bt] = HighlightComponent(str(bt)[13:], position, self.button_size,
                                                         is_highlighted=highlight)
            position -= Vector(0, self.button_size.y)

    def build_func(self, game_state):
        building_type = None
        for bt in self.building_types:
            if self.building_types[bt].is_highlighted:
                building_type = bt
        game_state.building_manager.spawn_building(game_state, game_state.tile_map.highlighted_tile, building_type)

    @staticmethod
    def upgrade_func(game_state):
        pass

    def render_background(self):
        batch = pyglet.graphics.Batch()
        color = (0, 255, 0)
        Renderer.colored_rectangle(batch, color, self.position, self.background_size)
        batch.draw()

    def render(self):
        if not self.visible:
            return

        self.render_background()
        for component in self.components:
            self.components[component].render(self.position)

        for bt in self.building_types:
            self.building_types[bt].render(self.position)

    def update(self, game_state):
        if not self.visible:
            return

        self.background_size = Vector(self.background_size.x, game_state.window_size.y)
        self.position = Vector(game_state.window_size.x - self.background_size.x, 0)

        if game_state.tile_map.highlighted_tile in game_state.building_manager.buildings:
            self.components['build_button'].visible = False
            self.components['upgrade_button'].visible = True
        else:
            self.components['build_button'].visible = True
            self.components['upgrade_button'].visible = False

        process_clicks(game_state, self.mouse_click_handler, False, self.position)

    def highlight_building(self, building_type):
        for bt in self.building_types:
            if bt != building_type:
                self.building_types[bt].is_highlighted = False

    def mouse_click_handler(self, game_state, click: MouseClick) -> bool:
        for component in self.components:
            if self.components[component].is_clicked(click):
                self.handlers[component](game_state)
                return True

        for bt in self.building_types:
            if self.building_types[bt].is_clicked(click):
                self.highlight_building(bt)
                return True

        return rect_contains_point(click.position, Vector(0, game_state.window_size.y), self.background_size)
