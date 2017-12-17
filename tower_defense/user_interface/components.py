from enum import Enum

import pyglet

from helper import Vector, KeyPresses, rect_contains_point, MouseClick


class TextComponent:
    def __init__(self, text: str, position: Vector, size: Vector, font_size: int = 25, visible: bool = True):
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
