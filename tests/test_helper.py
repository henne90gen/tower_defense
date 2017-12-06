import unittest

from helper import Vector


class VectorTest(unittest.TestCase):
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
