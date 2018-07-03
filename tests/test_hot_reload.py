import unittest
import os
from tower_defense.hot_reload import reload_all

script_path = os.path.dirname(os.path.realpath(__file__))


def write_module(file_name, time):
    with open(file_name, "w") as f:
        f.write(f"""
def my_function():
    return {time}
""")
    # FIXME this seems like a hack, why does 'open' not do this automatically?
    os.utime(file_name, (os.stat(file_name).st_atime,
                         os.stat(file_name).st_mtime + time))


class HotReloadTest(unittest.TestCase):
    def setUp(self):
        global __package__
        __package__ = "tests"

    def test_normal_reload(self):
        file_name = os.path.join(script_path, 'my_module_normal.py')
        time = 10
        write_module(file_name, time)
        self.assertTrue(os.path.exists(file_name))

        import tests.my_module_normal
        self.assertEqual(time, tests.my_module_normal.my_function())

        time = 42
        write_module(file_name, time)

        reload_all(['tests.my_module_normal'])
        self.assertEqual(time, tests.my_module_normal.my_function())

    def test_relative_import(self):
        file_name = os.path.join(script_path, 'my_module_relative.py')
        time = 10
        write_module(file_name, time)
        self.assertTrue(os.path.exists(file_name))

        from .my_module_relative import my_function
        self.assertEqual(time, my_function())

        time = 42
        write_module(file_name, time)

        reload_all(['tests.my_module_relative'])
        self.assertEqual(time, my_function())

    def test_multiple_relative_import(self):
        directory_path = os.path.join(script_path, 'sub_directory')
        if not os.path.exists(directory_path):
            os.mkdir(directory_path)
        init_path = os.path.join(directory_path, '__init__.py')
        with open(init_path, 'w') as f:
            f.write("")
        file_path = os.path.join(
            directory_path, 'my_module_multiple_relative.py')
        time = 10
        write_module(file_path, time)

        from .sub_directory.my_module_multiple_relative import my_function
        self.assertEqual(time, my_function())

        time = 42
        write_module(file_path, time)

        reload_all(['tests.sub_directory.my_module_multiple_relative'])
        self.assertEqual(time, my_function())
