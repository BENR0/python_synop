synop
===========

Package to parse SYNOP reports.


Description
-----------


Installation
------------
Download or clone the repository. cd into the directory and install with:
```
pip install -e .
```

Usage
-----

Todo
----
- plausibility checks between groups
    - e.g. cloud height in 8NChh is <30m and fog events
- handling of classes for contious variables (e.g. cloud height 0-49m etc.)
    - add additional information if value is a class or contious (se)
- translate code classes to english with wmo code tables
- add exceptions from the wmo manual of codes for group "rules" to methods
- check conversion of wind direction angles (also add conversion of angles to words for printing)
- add decoding of special weather conditions in 9SSss group of section 3

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

