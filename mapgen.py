import ror_zip_file
import osm
import bbox
import sys

if len(sys.argv) < 2:
    print("\nUsage: " + sys.argv[0] + " north,west,south,east")
    print("north,west,south,east are GPS coordinates of the bounding box used to create a map")
    print("Eg: mapgen.py 48.87814394530428,2.2821558610475257,48.86862582223842,2.3059560444047054")
    sys.exit(0)

coord = sys.argv[1].split(',')

north = float(coord[0])
south = float(coord[2])
west = float(coord[1])
east = float(coord[3])

if north > south:
    t = south
    south = north
    north = t
if west > east:
    t = west
    west = east
    east = t

bbox.coord = {"north": north, "south": south, "west": west, "east": east}
print("Bounding box:", bbox.coord)

ror_zip_file.create_default_file()
ror_zip_file.create_base()

osm.add_data_to_output_file()

