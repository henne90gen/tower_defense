from enum import Enum

import pyglet

from graphics import render_colored_rectangle, render_rectangle_border
from helper import Vector, KeyPresses, rect_contains_point, MouseClick


class TextComponent:
    def __init__(self, text: str, position: Vector, size: Vector, font_size: int = 25, visible: bool = True,
                 disabled: bool = False):
        self.text = text
        self.position = position
        self.size = size
        self.label = pyglet.text.Label(self.text,
                                       font_name='DejaVuSans',
                                       font_size=font_size,
                                       color=(255, 0, 255, 255),
                                       width=self.size.x, height=self.size.y,
                                       anchor_x='center', anchor_y='center')
        self.visible = visible
        self.disabled = disabled

    def toggle_visibility(self):
        self.visible = not self.visible

    def is_clicked(self, mouse_click: MouseClick) -> bool:
        if not self.visible:
            return False
        return rect_contains_point(mouse_click.position, self.position, self.size)

    def render(self, offset: Vector):
        if not self.visible:
            return

        pos = self.position + offset
        self.label.begin_update()
        self.label.x = pos.x + self.size.x / 2
        self.label.y = pos.y - self.size.y / 2
        self.label.text = self.text
        if self.disabled:
            self.label.color = (100, 0, 100, 100)
        else:
            self.label.color = (255, 0, 255, 255)
        self.label.end_update()

        bottom_right = Vector(pos.x + self.size.x, pos.y - self.size.y)
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, (
            'v2f', [pos.x, pos.y, bottom_right.x, pos.y, bottom_right.x, bottom_right.y, pos.x, bottom_right.y]))
        self.label.draw()


class Input(TextComponent):
    def __init__(self, position: Vector, size: Vector, font_size: int = 25, visible: bool = True,
                 has_focus: bool = False):
        super().__init__("", position, size, font_size, visible)
        self.has_focus = has_focus

    def is_clicked(self, mouse_click):
        if super().is_clicked(mouse_click):
            self.has_focus = True
            return True
        return False

    def add_text(self, key_presses: KeyPresses):
        if not self.has_focus:
            return

        if key_presses.back_space:
            self.text = self.text[:-1]
        else:
            self.text = self.text + key_presses.text


class HighlightComponent(TextComponent):
    def __init__(self, text: str, position: Vector, size: Vector, font_size: int = 25, visible: bool = True,
                 is_highlighted: bool = False):
        super().__init__(text, position, size, font_size, visible)
        self.is_highlighted = is_highlighted

    def is_clicked(self, mouse_click):
        if super().is_clicked(mouse_click):
            self.is_highlighted = True
            return True
        return False

    def render(self, offset: Vector):
        if not self.visible:
            return

        super().render(offset)
        self.render_highlight(offset)

    def render_highlight(self, offset: Vector):
        if not self.is_highlighted:
            return

        position = self.position + offset - Vector(0, self.size.y)

        batch = pyglet.graphics.Batch()
        render_rectangle_border(batch, position, self.size)
        batch.draw()
