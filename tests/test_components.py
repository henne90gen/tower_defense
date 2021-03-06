import unittest

from tower_defense.helper import Vector, MouseClick, KeyPresses
from tower_defense.user_interface.components import Button, Label, Input, HighlightableLabel


class ButtonTest(unittest.TestCase):
    def test_is_clicked(self):
        click = MouseClick()
        click.position = Vector(1, 1)

        text_component = Button("Hello", Vector(0, 10), Vector(10, 10))
        self.assertTrue(text_component.is_clicked(click))

        text_component = Button("Hello", Vector(
            0, 10), Vector(10, 10), visible=False)
        self.assertFalse(text_component.is_clicked(click))

        text_component = Button("Hello", Vector(), Vector(10, 10))
        self.assertFalse(text_component.is_clicked(click))


class LabelTest(unittest.TestCase):
    def test_render(self):
        was_called = []

        def dummy():
            was_called.append(0)

        text_component = Label("Hello", Vector(), Vector())
        text_component._label.draw = dummy
        text_component.render(Vector())
        self.assertEqual(1, len(was_called))

        text_component.visible = False
        text_component.render(Vector())
        self.assertEqual(1, len(was_called))

    def test_toggle_visibility(self):
        text_component = Label("Hello", Vector(), Vector())
        text_component.toggle_visibility()
        self.assertFalse(text_component.visible)


class InputTest(unittest.TestCase):
    def test_is_clicked(self):
        click = MouseClick()
        click.position = Vector(1, 1)

        input_component = Input(Vector(0, 10), Vector(10, 10))
        input_component.is_clicked(click)
        self.assertTrue(input_component.has_focus)

        input_component = Input(Vector(), Vector(10, 10))
        input_component.is_clicked(click)
        self.assertFalse(input_component.has_focus)

    def test_add_text(self):
        key_presses = KeyPresses()
        key_presses.text = ""

        input_component = Input(Vector(), Vector())
        input_component.add_text(key_presses)
        self.assertEqual(0, len(input_component.text))

        key_presses.text = "test"
        input_component = Input(Vector(), Vector())
        input_component.add_text(key_presses)
        self.assertEqual(0, len(input_component.text))

        key_presses.text = "test"
        input_component = Input(Vector(), Vector(), has_focus=True)
        input_component.add_text(key_presses)
        self.assertEqual("test", input_component.text)

        key_presses.back_space = True
        input_component = Input(Vector(), Vector(), has_focus=True)
        input_component.update(text="test")
        input_component.add_text(key_presses)
        self.assertEqual("tes", input_component.text)


class HighlightComponentTest(unittest.TestCase):
    def test_is_clicked(self):
        click = MouseClick()
        click.position = Vector(1, 1)

        highlight_component = HighlightableLabel(
            "", Vector(0, 10), Vector(10, 10))
        highlight_component.is_clicked(click)
        self.assertTrue(highlight_component.is_highlighted)

        highlight_component = HighlightableLabel("", Vector(), Vector(10, 10))
        highlight_component.is_clicked(click)
        self.assertFalse(highlight_component.is_highlighted)

    def test_render(self):
        was_called = []

        def dummy(*args):
            was_called.append(0)

        highlight_component = HighlightableLabel(
            "", Vector(), Vector(10, 10), visible=False)
        highlight_component.render_highlight = dummy
        highlight_component.render(Vector())
        self.assertEqual(0, len(was_called))

        highlight_component = HighlightableLabel("", Vector(), Vector(10, 10))
        highlight_component.render_highlight = dummy
        highlight_component.render(Vector())
        self.assertEqual(1, len(was_called))

    @staticmethod
    def test_render_highlight():
        highlight_component = HighlightableLabel("", Vector(), Vector(10, 10))
        highlight_component.render_highlight(Vector())

        highlight_component = HighlightableLabel("", Vector(), Vector(10, 10))
        highlight_component.is_highlighted = True
        highlight_component.render_highlight(Vector())
