from unittest import main, TextTestRunner

import sys

import os

if __name__ == '__main__':
    args = ["python -m unittest discover tests"]
    sys.path.append(os.path.join(os.getcwd(), 'tower_defense'))
    main(argv=args, module=None, testRunner=TextTestRunner)
