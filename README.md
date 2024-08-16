# mapgen
Proof of concept of a map generator for Rigs of Rods.
This has been tested on Linux only. Feedbacks for other systems are welcome.

# Dependencies:

*Overpy*: https://pypi.org/project/overpy/

pip install overpy

*bmi-topography*: https://bmi-topography.readthedocs.io/en/latest/

pip install topography

*OgreXMLConverter* executable must be in the user's PATH environment variable

- sudo apt install ogre-1.12-tools
or
- https://forum.rigsofrods.org/resources/ogre-command-line-tools.967/

# Usage:
    mapgen.py [config.json parameters overload]

Without parameters, mapgen use parameters in config.json file.
Every parameters in this file can be overloaded on the command line with <parameter>=<value>

The most useful parameters are:

 - map_name: name of map generated.
 - coord: latitude,longitude of the center of the map.
 - map_size: Map's size in meter (maps are always square). This must be a power of 2.
 - map_precision: Map's precision in meter. This must be a power of 2.
 - export_path: Where to write the resulting zip file.
 - api_key: If provided, the map use height map. Get your API key here: https://opentopography.org/.
 
### Eg:
Paris:
    python3 mapgen.py map_name=mapgen_paris coord=48.858550270756076,2.294099690364275 map_size=1024 map_precision=1

Singapore:
    python3 mapgen.py map_name=mapgen_singapore coord=1.2866844972308469,103.85945353238746 map_size=2048 map_precision=1

Mount Everest:
    Replace XXXXXX by an Open Topography API key that you can get from https://opentopography.org/
    python3 mapgen.py map_name=mapgen_everest coord=27.987930283715425,86.92536128772278 map_size=16384 map_precision=16 world_ground=snow generate_road=False api_key=XXXXXX

Grand Canyon:
    Replace XXXXXX by an Open Topography API key that you can get from https://opentopography.org/
    python3 mapgen.py map_name=mapgen_grand_canyon coord=36.099639286358254,-112.11247353296902 map_size=8192 map_precision=8 world_ground=red_dirt water_line=1.5 generate_road=False api_key=XXXXXX
