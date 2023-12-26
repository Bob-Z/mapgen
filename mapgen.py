import config
import helper
import ror_zip_file
import osm
import bbox
import sys
import osm_node
import osm_way
import ogre_material
import gvar


def process_relation(result):
    print("No relation is processed yet")


if len(sys.argv) < 2:
    print("\nUsage: " + sys.argv[0] + " <north,west,south,east>")
    print("<north,west,south,east> are latitudes and longitudes of the bounding box used to create a map")
    print("Eg: " + sys.argv[0] + " 48.87814394530428,2.2821558610475257,48.86862582223842,2.3059560444047054")
    print("The created map is called \"mapgen\"")
    sys.exit(0)

print("Work path:", config.config["work_path"])

if "export_path" in config.config:
    gvar.EXPORT_PATH = config.config["export_path"]
print("Export path: ", gvar.EXPORT_PATH)

coord = sys.argv[1].split(',')

north = float(coord[0])
south = float(coord[2])
west = float(coord[1])
east = float(coord[3])

if north < south:
    t = south
    south = north
    north = t
if west > east:
    t = west
    west = east
    east = t


bbox.coord = {"north": north, "south": south, "west": west, "east": east}
bbox.coordXY = {"north": helper.lat_to_x(north), "south": helper.lat_to_x(south), "west": helper.lon_to_y(west), "east": helper.lon_to_y(east)}
print("Bounding box:", bbox.coord)

osm_data = osm.get_data()

ror_zip_file.create_default_file()
ror_zip_file.write_default_file()

osm_node.process(osm_data)
osm_way.process(osm_data)
process_relation(osm_data)

ror_zip_file.add_file(config.config["map_name"] + ".tobj")
ogre_material.add_file()
