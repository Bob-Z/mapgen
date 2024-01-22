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

mapgen.py <north,west,south,east>


<north,west,south,east> are latitude and longitude of the bounding box used to create a map


### Eg:
$ python3 mapgen.py 37.9907054802653,23.712457618520016,37.982217352248156,23.726836182108038

### You will see the following output:

Work path: ./work/
Export path:  /home/user/.rigsofrods/mods/
Bounding box: {'north': 37.9907054802653, 'south': 37.982217352248156, 'west': 23.712457618520016, 'east': 23.726836182108038}
Requesting OpenStreetMap
Done in 0.9532103538513184 seconds

Writing OpenStreetMap cache file

Map size:  1260.0496293634865 x 943.8367641227754
Dumping OSM data in ./log/osm_request.txt
Generating sea...
No sea
Processing nodes...
nodes:  18350 / 18350 
Processing relations...
relations:  175 / 175 
Processing ways...
ways:  3582 / 3582 

Total  nodes  =  18350
Empty  nodes   =  16909
Ignored  nodes   =  0
Complete  nodes   =  94
Incomplete  nodes  =  80
Not processed  nodes  =  1267

Total  ways  =  3582
Empty  ways   =  34
Ignored  ways   =  53
Complete  ways   =  2675
Incomplete  ways  =  700
Not processed  ways  =  120

Total  relations  =  175
Empty  relations   =  0
Ignored  relations   =  10
Complete  relations   =  13
Incomplete  relations  =  5
Not processed  relations  =  147

### Then run Rigs of Rods with map called "mapgen"

./RunRoR -map mapgen