import os
from typing import List, Optional, Dict

import pyglet

from ..game_types import BuildingType
from ..graphics import Renderer
from ..helper import Vector, MouseClick, process_clicks, rect_contains_point, get_maps_path
from .components import Input, Label, Button, HighlightableLabel


class Dialog:
    def __init__(self, visible: bool) -> None:
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
        game_state.key_presses.up = False
        game_state.key_presses.down = False
        game_state.key_presses.left = False
        game_state.key_presses.right = False


class NewMapDialog(Dialog):
    def __init__(self, visible: bool = False) -> None:
        super().__init__(visible)
        self.position = Vector(200, 0)
        text_width = 150
        text_height = 40
        self.labels: Dict[str, Label] = {
            'width': Label("Width:", Vector(0, 0), Vector(text_width, text_height)),
            'height': Label("Height:", Vector(0, -text_height), Vector(text_width, text_height)),
            'name': Label("Name:", Vector(0, -text_height * 2), Vector(text_width, text_height)),
        }
        self.inputs: Dict[str, Input] = {
            'width': Input(Vector(text_width, 0), Vector(300, text_height), has_focus=True),
            'height': Input(Vector(text_width, -text_height), Vector(300, text_height)),
            'name': Input(Vector(text_width, -text_height * 2), Vector(300, text_height)),
        }
        self.buttons: Dict[str, Button] = {
            'submit': Button("Create", Vector(0, -text_height * 3), Vector(text_width, text_height)),
            'cancel': Button("Cancel", Vector(text_width, -text_height * 3), Vector(text_width, text_height))
        }

        self.handlers = {
            'submit': self.submit_func,
            'cancel': self.cancel_func
        }

    def open(self, game_state):
        super().open(game_state)
        self.inputs['width'].update(text="10")
        self.inputs['height'].update(text="10")
        self.inputs['name'].update(text="")

    def render(self):
        if self.visible:
            for label in self.labels:
                self.labels[label].render(self.position)
            for input_ in self.inputs:
                self.inputs[input_].render(self.position)
            for button in self.buttons:
                self.buttons[button].render(self.position)

    def submit_func(self, game_state):
        try:
            new_width = int(self.inputs['width'].text)
            new_height = int(self.inputs['height'].text)
        except Exception as e:
            print(e)
            return
        if self.inputs['name'].text:
            file_name = os.path.join(
                get_maps_path(), self.inputs['name'].text + '.map')
            game_state.tile_map.new(game_state, file_name,
                                    Vector(new_width, new_height))
        self.visible = False

    def cancel_func(self, _):
        self.visible = False

    def update(self, game_state):
        super().update(game_state)

        for input_ in self.inputs:
            self.inputs[input_].add_text(game_state.key_presses)

        process_clicks(game_state, self.mouse_click_handler,
                       False, self.position)

    def mouse_click_handler(self, game_state, click: MouseClick) -> bool:
        for button in self.buttons:
            if self.buttons[button].is_clicked(click):
                self.handlers[button](game_state)
                return True
        for input_ in self.inputs:
            if self.inputs[input_].is_clicked(click):
                self.give_exclusive_focus(input_)
                return True
        return False

    def give_exclusive_focus(self, input_: str):
        for other_input in self.inputs:
            if input_ == other_input:
                continue
            self.inputs[other_input].has_focus = False


class LoadMapDialog(Dialog):
    def __init__(self, visible: bool = False) -> None:
        super().__init__(visible)
        self.maps: List[Button] = []
        self.cancel_button: Optional[Button] = None

    def refresh_maps(self, maps_path: str):
        self.maps = []
        current_index = 0
        height = 50
        for file in os.listdir(maps_path):
            if '.map' in file:
                text_component = Button(file, Vector(
                    150, 100 - height * current_index), Vector(300, height))
                self.maps.append(text_component)
                current_index += 1
        return current_index, height

    def update_cancel_button(self, current_index, height):
        self.cancel_button = Button("Cancel", Vector(
            150, 100 - height * current_index), Vector(200, height))

    def open(self, game_state):
        super().open(game_state)
        current_index, height = self.refresh_maps(get_maps_path())
        self.update_cancel_button(current_index, height)

    def update(self, game_state):
        super().update(game_state)
        process_clicks(game_state, self.mouse_click_handler,
                       False, self.position)

    def mouse_click_handler(self, game_state, click):
        if self.cancel_button.is_clicked(click):
            self.visible = False
            return True
        for tile_map in self.maps:
            if tile_map.is_clicked(click):
                file_name = os.path.join(get_maps_path(), tile_map.text)
                game_state.tile_map.load(game_state, file_name)
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
            'build_button': Button("Build", Vector(0, self.button_size.y), self.button_size),
            'upgrade_button': Button("Upgrade", Vector(0, self.button_size.y), self.button_size, visible=False)
        }
        self.handlers = {
            'build_button': self.build_func,
            'upgrade_button': self.upgrade_func
        }
        self.building_types = {
            BuildingType.LASER: HighlightableLabel("", Vector(), Vector()),
            BuildingType.HAMMER: HighlightableLabel("", Vector(), Vector()),
        }
        # self.upgrade_buttons = {}

    def open(self, game_state):
        super().open(game_state)
        self.position = Vector()

        position = Vector(0, game_state.window_size.y)
        for index, bt in enumerate(BuildingType):
            highlight = index == 0
            self.building_types[bt] = HighlightableLabel(str(bt)[13:], position, self.button_size,
                                                         is_highlighted=highlight)
            position -= Vector(0, self.button_size.y)

    def build_func(self, game_state):
        building_type = None
        for bt in self.building_types:
            if self.building_types[bt].is_highlighted:
                building_type = bt
        game_state.building_manager.spawn_building(
            game_state, game_state.tile_map.highlighted_tile, building_type)

    @staticmethod
    def upgrade_func(game_state):
        pass

    def render_background(self):
        batch = pyglet.graphics.Batch()
        color = (0, 255, 0)
        Renderer.colored_rectangle(
            batch, color, self.position, self.background_size)
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

        self.background_size = Vector(
            self.background_size.x, game_state.window_size.y)
        self.position = Vector(
            game_state.window_size.x - self.background_size.x, 0)

        if game_state.tile_map.highlighted_tile in game_state.building_manager.buildings:
            self.components['build_button'].visible = False
            self.components['upgrade_button'].visible = True
        else:
            self.components['build_button'].visible = True
            self.components['upgrade_button'].visible = False

        process_clicks(game_state, self.mouse_click_handler,
                       False, self.position)

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
