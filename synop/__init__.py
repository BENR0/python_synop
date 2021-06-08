#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from synop.version import version as __version__
except ImportError:
    from pkg_resources import get_distribution
    __version__ = get_distribution(__name__).version
