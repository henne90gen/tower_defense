import unittest

from game_state import GameState
from helper import Vector, MouseClick
from user_interface.dialogs import Dialog, NewMapDialog, LoadMapDialog


class Object(object):
    pass


class DialogTest(unittest.TestCase):
    @staticmethod
    def test_render():
        dialog = Dialog(True)
        dialog.render()

    def test_update(self):
        game_state = GameState()
        game_state.key_presses.up = True
        game_state.key_presses.down = True
        game_state.key_presses.left = True
        game_state.key_presses.right = True
        dialog = Dialog(True)
        dialog.update(game_state)
        self.assertFalse(game_state.key_presses.up)
        self.assertFalse(game_state.key_presses.down)
        self.assertFalse(game_state.key_presses.left)
        self.assertFalse(game_state.key_presses.right)

    def test_open(self):
        game_state = GameState()
        game_state.window_size = Vector(0, 500)
        dialog = Dialog(True)
        dialog.open(game_state)
        self.assertTrue(dialog.visible)
        self.assertEqual(300, dialog.position.y)


class NewMapDialogTest(unittest.TestCase):
    def test_render(self):
        was_called = []

        def dummy(_):
            was_called.append(0)

        test_object = Object()
        test_object.render = dummy
        new_map_dialog = NewMapDialog()
        new_map_dialog.components = {"test": test_object}
        new_map_dialog.render()
        self.assertEqual(0, len(was_called))

        new_map_dialog = NewMapDialog(visible=True)
        new_map_dialog.components = {"test": test_object}
        new_map_dialog.render()
        self.assertEqual(1, len(was_called))

    def test_update(self):
        game_state = GameState()
        was_called = []

        def dummy(_):
            was_called.append(0)

        test_object = Object()
        test_object.add_text = dummy

        new_map_dialog = NewMapDialog()
        new_map_dialog.components = {"test": test_object}
        new_map_dialog.update(game_state)
        self.assertEqual(0, len(was_called))

        new_map_dialog = NewMapDialog()
        new_map_dialog.components = {"test_input": test_object}
        new_map_dialog.update(game_state)
        self.assertEqual(1, len(was_called))

    def test_give_exclusive_focus(self):
        test_object1 = Object()
        test_object1.has_focus = True

        test_object2 = Object()
        test_object2.has_focus = True

        new_map_dialog = NewMapDialog()
        new_map_dialog.components = {"test1_input": test_object1, "test2_input": test_object2}
        new_map_dialog.give_exclusive_focus("test1_input")
        self.assertFalse(test_object2.has_focus)
        self.assertTrue(test_object1.has_focus)

    def test_cancel_func(self):
        new_map_dialog = NewMapDialog()
        new_map_dialog.cancel_func(None)
        self.assertFalse(new_map_dialog.visible)

    def test_submit_func(self):
        was_called = []

        def dummy(game_state, path, size):
            was_called.append(0)

        game_state = GameState()
        game_state.tile_map = Object()
        game_state.tile_map.new = dummy
        width_input = Object()
        width_input.text = "5"
        height_input = Object()
        height_input.text = "5"
        name_input = Object()
        name_input.text = "test"

        new_map_dialog = NewMapDialog()
        new_map_dialog.components = {"width_input": width_input, "height_input": height_input, "name_input": name_input}
        new_map_dialog.submit_func(game_state)
        self.assertFalse(new_map_dialog.visible)
        self.assertEqual(1, len(was_called))

        was_called.clear()
        width_input = Object()
        width_input.text = ""
        height_input = Object()
        height_input.text = "5"
        name_input = Object()
        name_input.text = "test"

        new_map_dialog = NewMapDialog()
        new_map_dialog.components = {"width_input": width_input, "height_input": height_input, "name_input": name_input}
        new_map_dialog.submit_func(game_state)
        self.assertFalse(new_map_dialog.visible)
        self.assertEqual(0, len(was_called))

        was_called.clear()
        width_input = Object()
        width_input.text = "5"
        height_input = Object()
        height_input.text = ""
        name_input = Object()
        name_input.text = "test"

        new_map_dialog = NewMapDialog()
        new_map_dialog.components = {"width_input": width_input, "height_input": height_input, "name_input": name_input}
        new_map_dialog.submit_func(game_state)
        self.assertFalse(new_map_dialog.visible)
        self.assertEqual(0, len(was_called))

        was_called.clear()
        width_input = Object()
        width_input.text = "5"
        height_input = Object()
        height_input.text = "5"
        name_input = Object()
        name_input.text = ""

        new_map_dialog = NewMapDialog()
        new_map_dialog.components = {"width_input": width_input, "height_input": height_input, "name_input": name_input}
        new_map_dialog.submit_func(game_state)
        self.assertFalse(new_map_dialog.visible)
        self.assertEqual(0, len(was_called))

    def test_open(self):
        game_state = GameState()
        width_input = Object()
        width_input.text = "5"
        height_input = Object()
        height_input.text = "5"
        name_input = Object()
        name_input.text = ""

        new_map_dialog = NewMapDialog()
        new_map_dialog.components = {"width_input": width_input, "height_input": height_input, "name_input": name_input}
        new_map_dialog.open(game_state)
        self.assertTrue(new_map_dialog.visible)
        self.assertEqual("", width_input.text)
        self.assertEqual("", height_input.text)
        self.assertEqual("", name_input.text)

    def test_mouse_click_handler(self):
        game_state = GameState()
        click = MouseClick()
        click.position = Vector()

        was_called = []

        def dummy(*args):
            was_called.append(0)
            return True

        new_map_dialog = NewMapDialog()
        actual = new_map_dialog.mouse_click_handler(game_state, click)
        self.assertFalse(actual)

        width_input = Object()
        width_input.text = "5"
        width_input.is_clicked = dummy

        new_map_dialog = NewMapDialog()
        new_map_dialog.give_exclusive_focus = dummy
        new_map_dialog.components = {"width_input": width_input}
        actual = new_map_dialog.mouse_click_handler(game_state, click)
        self.assertTrue(actual)
        self.assertEqual(2, len(was_called))

        button = Object()
        button.text = "5"
        button.is_clicked = dummy

        was_called.clear()
        new_map_dialog = NewMapDialog()
        new_map_dialog.give_exclusive_focus = dummy
        new_map_dialog.components = {"submit_button": button}
        actual = new_map_dialog.mouse_click_handler(game_state, click)
        self.assertTrue(actual)
        self.assertEqual(1, len(was_called))


class LoadMapDialogTest(unittest.TestCase):
    @staticmethod
    def test_update():
        game_state = GameState()
        load_map_dialog = LoadMapDialog()
        load_map_dialog.update(game_state)

    def test_refresh_maps(self):
        load_map_dialog = LoadMapDialog()
        load_map_dialog.refresh_maps("./tests/maps")
        self.assertEqual(1, len(load_map_dialog.maps))
        self.assertEqual("test.map", load_map_dialog.maps[0].text)

    def test_open(self):
        game_state = GameState()
        was_called = []

        def dummy(*args):
            was_called.append(0)
            return 0, 0

        load_map_dialog = LoadMapDialog()
        load_map_dialog.refresh_maps = dummy
        load_map_dialog.open(game_state)
        self.assertEqual(1, len(was_called))

    def test_render(self):
        was_called = []

        def dummy(*args):
            was_called.append(0)

        test_map = Object()
        test_map.render = dummy

        load_map_dialog = LoadMapDialog(True)
        load_map_dialog.cancel_button = Object()
        load_map_dialog.cancel_button.render = dummy
        load_map_dialog.maps = [test_map]
        load_map_dialog.render()
        self.assertEqual(2, len(was_called))

    def test_mouse_click_handler(self):
        was_called = []
        game_state = GameState()
        click = Object()

        def dummy_true(*args):
            was_called.append(0)
            return True

        def dummy_false(*args):
            was_called.append(0)
            return False

        load_map_dialog = LoadMapDialog()
        load_map_dialog.cancel_button = Object()
        load_map_dialog.cancel_button.is_clicked = dummy_false
        actual = load_map_dialog.mouse_click_handler(game_state, click)
        self.assertFalse(actual)
        self.assertEqual(1, len(was_called))

        was_called.clear()
        load_map_dialog = LoadMapDialog()
        load_map_dialog.cancel_button = Object()
        load_map_dialog.cancel_button.is_clicked = dummy_true
        actual = load_map_dialog.mouse_click_handler(game_state, click)
        self.assertTrue(actual)
        self.assertEqual(1, len(was_called))

        was_called.clear()
        test_map = Object()
        test_map.text = "test"
        test_map.is_clicked = dummy_true
        load_map_dialog = LoadMapDialog()
        load_map_dialog.cancel_button = Object()
        load_map_dialog.cancel_button.is_clicked = dummy_false
        load_map_dialog.maps = [test_map]
        actual = load_map_dialog.mouse_click_handler(game_state, click)
        self.assertTrue(actual)
        self.assertEqual(2, len(was_called))
