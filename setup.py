try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from synop import __version__

config = {
    "name": "synop",
    "version": __version__,
    "author": "Benjamin Roesner",
    "description": "Packege to parse SYNOP reports",
    "url": "https://github.com/BENR0/python_synop",
    "download_url": "https://github.com/BENR0/python_synop",
    "author_email": ".",
    "install_requires": [],
    "packages": ["synop"],
    "scripts": [],
}

setup(**config)

