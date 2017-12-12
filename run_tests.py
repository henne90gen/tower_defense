from unittest import main, TextTestRunner

import sys

import os

args = ["python -m unittest discover tests"]
sys.path.append(os.path.join(os.getcwd(), 'tower_defense'))
main(argv=args, module=None, testRunner=TextTestRunner)
