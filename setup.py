#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup file for synop."""

from setuptools import setup, find_packages

try:
    # HACK: https://github.com/pypa/setuptools_scm/issues/190#issuecomment-351181286
    # Stop setuptools_scm from including all repository files
    import setuptools_scm.integration
    setuptools_scm.integration.find_files = lambda _: []
except ImportError:
    pass

README = open("README.rst", "r").read()

setup(
    name="synop",
    author="Benjamin Rösner",
    author_email=".",
    description="Parse SYNOP reports",
    long_description=README,
    url="https://github.com/benr0/python_synop",
    packages=find_packages(),
    python_requires=">=3.7",
    zip_safe=False,
    use_scm_version={"write_to": "synop/version.py"},
    setup_requires=["setuptools_scm"],
    install_requires=["numpy>=1.16.5",
                      "pandas"],
    extras_require={"test": ["pytest"]},
    classifiers=["Programming Language :: Python",
                 "Development Status :: 4 - Beta",
                 "Intended Audience :: Science/Research",
                 "License :: OSI Approved :: GNU General Public License v3 " +
                 "or later (GPLv3+)",
                 "Operating System :: OS Independent",
                 "Topic :: Scientific/Engineering"],
)
