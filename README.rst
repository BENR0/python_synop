Synop
============

.. image:: https://travis-ci.com/BENR0/python_synop.svg?branch=master
    :target: https://travis-ci.com/BENR0/python_synop

.. image:: https://codecov.io/gh/BENR0/python_synop/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/BENR0/python_synop

.. image:: https://img.shields.io/github/license/BENR0/python_synop
    :target: https://opensource.org/licenses/GPL-3.0

Package to parse SYNOP reports.


Description
-----------
This package allows parsing and decoding of SYNOP reports as speciefied by the WMO.


Installation
------------
Currently the package is not available via PyPi in order to use it
download or clone the repository. cd into the directory and install with:
```
pip install -e .
```

Usage
-----
```python
from synop.synop import synop

report = "201809051400 AAXX 05141 10224 42680 50704 10230 20139 30174 40180 58010 81101 333 55309 22094 30345 81845 85080 91007 90710"

syn = synop(report)

#get all synop variables as a dict
syn.to_dict()
```
