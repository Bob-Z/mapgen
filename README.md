# mapgen
Map generator for Rigs of Rods from real world data

# Dependencies:

*Overpy*: https://pypi.org/project/overpy/

- sudo apt install python3-overpy
- pip install overpy

*OgreXMLConverter* executable must be in the user's PATH environnement variable

- https://forum.rigsofrods.org/resources/ogre-command-line-tools.967/

# Usage:

mapgen.py <north,west,south,east>


<north,west,south,east> are latitude and longitude of the bounding box used to create a map


Eg: mapgen.py 48.87814394530428,2.2821558610475257,48.86862582223842,2.3059560444047054"
