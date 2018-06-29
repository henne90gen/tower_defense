import pyglet
from ..graphics import Renderer
from ..helper import Vector, MouseClick, KeyPresses, rect_contains_point


class Widget:
    def __init__(self, position: Vector, size: Vector, visible: bool=True) -> None:
        self.position = position
        self.size = size
        self.visible = visible
        self._disabled = False

    @property
    def disabled(self):
        return self._disabled

    def toggle_visibility(self):
        self.visible = not self.visible

    def is_clicked(self, mouse_click: MouseClick) -> bool:
        return False

    def render(self, offset: Vector):
        pass


class Label(Widget):
    def __init__(self, text: str, position: Vector, size: Vector, font_size: int = 25, visible: bool=True) -> None:
        super().__init__(position, size, visible)
        self._text = text
        self._label = pyglet.text.Label(self._text,
                                        font_name='DejaVuSans',
                                        font_size=font_size,
                                        color=(255, 0, 255, 255),
                                        width=self.size.x, height=self.size.y,
                                        anchor_x='center', anchor_y='center')

    @property
    def text(self):
        return self._text

    def update(self, text: str = None, disabled: bool = None):
        updated = False

        if text is not None and text != self._text:
            self._text = text
            self._label.begin_update()
            self._label.text = self._text
            updated = True

        if disabled is not None and disabled != self._disabled:
            if not updated:
                self._label.begin_update()

            self._disabled = disabled
            if self._disabled:
                self._label.color = (100, 0, 100, 100)
            else:
                self._label.color = (255, 0, 255, 255)
            updated = True

        if updated:
            self._label.end_update()

    def render(self, offset: Vector):
        if not self.visible:
            return

        pos = self.position + offset
        self._label.x = pos.x + self.size.x / 2
        self._label.y = pos.y - self.size.y / 2

        bottom_right = Vector(pos.x + self.size.x, pos.y - self.size.y)
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, (
            'v2f', [pos.x, pos.y, bottom_right.x, pos.y, bottom_right.x, bottom_right.y, pos.x, bottom_right.y]))
        self._label.draw()


class HighlightableLabel(Label):
    def __init__(self, text: str, position: Vector, size: Vector, font_size: int = 25, visible: bool = True,
                 is_highlighted: bool = False) -> None:
        super().__init__(text, position, size, font_size, visible)
        self.is_highlighted = is_highlighted

    def is_clicked(self, mouse_click):
        if rect_contains_point(mouse_click.position, self.position, self.size):
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


class Button(Label):
    def __init__(self, text: str, position: Vector, size: Vector, font_size: int = 25, visible: bool=True) -> None:
        super().__init__(text, position, size, font_size, visible=visible)

    def is_clicked(self, mouse_click: MouseClick) -> bool:
        if not self.visible:
            return False
        return rect_contains_point(mouse_click.position, self.position, self.size)


class Input(Button):
    def __init__(self, position: Vector, size: Vector, font_size: int = 25, has_focus: bool = False) -> None:
        super().__init__("", position, size, font_size)
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
