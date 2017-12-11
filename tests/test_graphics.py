import unittest

from graphics import Textures


class TexturesTest(unittest.TestCase):
    def test_init(self):
        textures = Textures()
        textures.load('../tower_defense/res')
        self.assertIsNotNone(textures)
