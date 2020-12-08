
from setuptools import setup

setup(name='p2py',
      version='1.0',
      # list folders, not files
      packages=['src','src.test'],
      install_requires=['aiohttp', 'pytest'],
      )