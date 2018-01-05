import pyglet

from graphics import Renderer
from helper import Vector, KeyPresses, rect_contains_point, MouseClick


class TextComponent:
    def __init__(self, text: str, position: Vector, size: Vector, font_size: int = 25, visible: bool = True,
                 disabled: bool = False):
        self.visible = visible
        self._disabled = disabled
        self._text = text
        self.position = position
        self.size = size
        self.label = pyglet.text.Label(self._text,
                                       font_name='DejaVuSans',
                                       font_size=font_size,
                                       color=(255, 0, 255, 255),
                                       width=self.size.x, height=self.size.y,
                                       anchor_x='center', anchor_y='center')

    @property
    def disabled(self):
        return self._disabled

    @property
    def text(self):
        return self._text

    def toggle_visibility(self):
        self.visible = not self.visible

    def is_clicked(self, mouse_click: MouseClick) -> bool:
        if not self.visible:
            return False
        return rect_contains_point(mouse_click.position, self.position, self.size)

    def update(self, text: str = None, disabled: bool = None):
        updated = False

        if text and text != self._text:
            self._text = text
            self.label.begin_update()
            self.label.text = self._text
            updated = True

        if disabled is not None and disabled != self._disabled:
            self._disabled = disabled

            if not updated:
                self.label.begin_update()
            if self._disabled:
                self.label.color = (100, 0, 100, 100)
            else:
                self.label.color = (255, 0, 255, 255)

        if updated:
            self.label.end_update()

    def render(self, offset: Vector):
        if not self.visible:
            return

        pos = self.position + offset
        self.label.x = pos.x + self.size.x / 2
        self.label.y = pos.y - self.size.y / 2

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
            self.update(text=self.text[:-1])
        else:
            self.update(text=self.text + key_presses.text)


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
        Renderer.rectangle_border(batch, position, self.size)
        batch.draw()
