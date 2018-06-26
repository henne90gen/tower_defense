import unittest

import pyglet

from tower_defense.helper import Vector
from tower_defense.graphics import Textures, Renderer, MovementGroup


class Object(object):
    pass


class TexturesTest(unittest.TestCase):
    def test_init(self):
        textures = Textures()
        textures.load('./tower_defense/res')
        self.assertIsNotNone(textures)


class MethodTest(unittest.TestCase):
    def test_render_colored_rectangle(self):
        def add(count, mode, group, *data):
            self.assertEqual(4, count)
            self.assertEqual(pyglet.graphics.GL_QUADS, mode)
            self.assertEqual(MovementGroup, type(group))
            expected = (('v2f/static', [10, 0, 10, 10, 0, 10, 0, 0]),
                        ('c3B/static', (255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255)))
            self.assertEqual(expected, data)

        position = Vector()
        size = Vector(10, 10)
        color = (255, 255, 255)
        batch = Object()
        batch.add = add
        Renderer.colored_rectangle(batch, color, position, size)

    def test_render_textured_rectangle(self):
        def add(count, mode, group, *data):
            self.assertEqual(4, count)
            self.assertEqual(pyglet.graphics.GL_QUADS, mode)
            self.assertEqual("texture group", group)
            expected = (('v2f/static', [10, 0, 10, 10, 0, 10, 0, 0]), ('t2f/static', [1, 0, 1, 1, 0, 1, 0, 0]))
            self.assertEqual(expected, data)

        position = Vector()
        size = Vector(10, 10)
        texture = "texture group"
        batch = Object()
        batch.add = add
        Renderer.textured_rectangle(batch, texture, position, size, tex_max=1, tex_min=0)


class MovementGroupTest(unittest.TestCase):
    @staticmethod
    def test_set_state():
        group = MovementGroup(0, Vector())
        group.set_state()

    @staticmethod
    def test_unset_state():
        group = MovementGroup(0, Vector())
        group.unset_state()
