synop
===========

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


License
-------

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

