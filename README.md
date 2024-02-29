# mapgen
Proof of concept of a map generator for Rigs of Rods.
This has been tested on Linux only.

# Dependencies:

*Overpy*: https://pypi.org/project/overpy/

- sudo apt install python3-overpy
or
- pip install overpy

*OgreXMLConverter* executable must be in the user's PATH environment variable

- sudo apt install ogre-1.12-tools
or
- https://forum.rigsofrods.org/resources/ogre-command-line-tools.967/

# Usage:
    mapgen.py <latitude,longitude> <map size> <map precision>


- latitude,longitude: coordinate of the map's center.

- map size: Map is always square. This must be a power of 2. Default to 512 meters

- map precision: Map precision in meters. (size x precision) must be a power of 2. Can be less than 1.0, but not negative. Default to 1 meter

Default map name is "mapgen". This can be modified in config.json file

### Eg:
    python3 mapgen.py -15.408407657743856,28.280147286542533 256 0.5

### Then run Rigs of Rods with map called "mapgen"

    ./RunRoR -map mapgen