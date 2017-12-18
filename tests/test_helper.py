import unittest

from game_state import GameState
from tower_defense.helper import Vector, rect_contains_point, constrain_rect_to_bounds, MouseClick, process_clicks


class MouseClickTest(unittest.TestCase):
    def test_eq(self):
        mc1 = MouseClick()
        mc2 = MouseClick()
        self.assertEqual(mc1, mc2)
        self.assertNotEqual(mc1, "Not a mouse click")


class VectorTest(unittest.TestCase):
    def test_init(self):
        vec = Vector()
        self.assertEqual(0, vec.x)
        self.assertEqual(0, vec.y)

        vec = Vector(1, 2)
        self.assertEqual(1, vec.x)
        self.assertEqual(2, vec.y)

        vec = Vector(point=(1, 2))
        self.assertEqual(1, vec.x)
        self.assertEqual(2, vec.y)

    def test_add(self):
        vec1 = Vector(1, 2)
        vec2 = Vector(2, 3)
        self.assertEqual(Vector(3, 5), vec1 + vec2)
        self.assertEqual(Vector(3, 5), vec2 + vec1)

    def test_add_tuple(self):
        vec = Vector(1, 2)
        self.assertEqual(Vector(3, 5), vec + (2, 3))
        self.assertEqual(Vector(3, 5), (2, 3) + vec)

    def test_sub(self):
        vec1 = Vector(1, 2)
        vec2 = Vector(2, 3)
        self.assertEqual(Vector(-1, -1), vec1 - vec2)
        self.assertEqual(Vector(1, 1), vec2 - vec1)

    def test_sub_tuple(self):
        vec = Vector(1, 2)
        self.assertEqual(Vector(-1, -1), vec - (2, 3))
        self.assertEqual(Vector(1, 1), (2, 3) - vec)

    def test_mul(self):
        vec = Vector(1, 2)
        self.assertEqual(Vector(3, 6), vec * 3)

    def test_divide(self):
        vec = Vector(3, 6)
        self.assertEqual(Vector(1, 2), vec / 3)

    def test_floor_divide(self):
        vec = Vector(3, 6)
        self.assertEqual(Vector(1, 2), vec // 3)

    def test_not_equal(self):
        vec1 = Vector(1, 2)
        vec2 = Vector(3, 4)
        self.assertTrue(vec1 != vec2)

    def test_str(self):
        vec = Vector(1, 2)
        self.assertEqual("(1, 2)", str(vec))

    def test_length(self):
        vec = Vector()
        self.assertEqual(0, vec.length())

        vec = Vector(2, 0)
        self.assertEqual(2, vec.length())

        vec = Vector(3, 4)
        self.assertEqual(5, vec.length())


class MethodTest(unittest.TestCase):
    def test_rect_contains_point(self):
        point = Vector(10, 10)
        rect_position = Vector(0, 20)
        rect_size = Vector(20, 20)
        self.assertTrue(rect_contains_point(point, rect_position, rect_size))

        point = Vector(0, 0)
        rect_position = Vector(0, 20)
        rect_size = Vector(20, 20)
        self.assertFalse(rect_contains_point(point, rect_position, rect_size))

    def test_constrain_to_bounds(self):
        window_size = Vector(100, 100)
        position = Vector(50, 50)
        rect_size = Vector(10, 10)
        actual = constrain_rect_to_bounds(window_size, position, rect_size)
        self.assertEqual(position, actual)

        window_size = Vector(100, 100)
        position = Vector(100, 100)
        rect_size = Vector(10, 10)
        actual = constrain_rect_to_bounds(window_size, position, rect_size)
        self.assertEqual(Vector(50, 50), actual)

        window_size = Vector(100, 100)
        position = Vector(0, 0)
        rect_size = Vector(10, 10)
        actual = constrain_rect_to_bounds(window_size, position, rect_size)
        self.assertEqual(Vector(40, 40), actual)

    def test_process_clicks(self):
        game_state = GameState()
        game_state.mouse_clicks.append(MouseClick())

        def false_processor(game_state, mouse_click):
            return False

        process_clicks(game_state, false_processor)
        self.assertEqual(1, len(game_state.mouse_clicks))

        def offset_processor(game_state, mouse_click):
            self.assertEqual(Vector(-10, -10), mouse_click.position)
            return False

        process_clicks(game_state, offset_processor, map_to_world_space=False, offset=Vector(10, 10))
        self.assertEqual(1, len(game_state.mouse_clicks))

        def true_processor(game_state, mouse_click):
            return True

        process_clicks(game_state, true_processor)
        self.assertEqual(0, len(game_state.mouse_clicks))
