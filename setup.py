import os
from setuptools import setup


def read(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()


setup(
    name="tower-defense",
    version="0.0.1",
    author="Hendrik Müller",
    author_email="",
    packages=['tower-defense', 'tests'],
    install_requires=['pygame'],
    long_description=read('README.md'),
    description="Tower defense game",
)
