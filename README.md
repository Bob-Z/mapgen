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
    mapgen.py <latitude, longitude> <map size>


<latitude, longitude> coordinate of the map's center
<map size> Map is always square. This must be a power of 2. Default to 512 meters

Default map name is "mapgen". This can be modified in config.json file

### Eg:
    python3 mapgen.py 48.87814394530428,2.2821558610475257 1024

### Then run Rigs of Rods with map called "mapgen"

    ./RunRoR -map mapgen