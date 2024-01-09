# mapgen
Map generator

# Dependencies:

*Overpy*: https://pypi.org/project/overpy/

- sudo apt install python3-overpy
or
- pip install overpy

*OgreXMLConverter* executable must be in the user's PATH environnement variable

- sudo apt install ogre-1.12-tools
or
- https://forum.rigsofrods.org/resources/ogre-command-line-tools.967/

# Usage:

mapgen.py <north,west,south,east>


<north,west,south,east> are latitude and longitude of the bounding box used to create a map


Eg: python3 mapgen.py 48.87814394530428,2.2821558610475257,48.86862582223842,2.3059560444047054
