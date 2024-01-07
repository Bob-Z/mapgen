import config
import helper
import ror_zip_file
import osm
import bbox
import sys
import ogre_material
import gvar
import gen_barrier
import gen_building
import gen_land
import gen_water
import gen_road
import gen_sea
import gen_shelter
import gen_object
import osm_tags
import copy

if len(sys.argv) < 2:
    print("\nUsage: " + sys.argv[0] + " <north,west,south,east>")
    print("<north,west,south,east> are latitudes and longitudes of the bounding box used to create a map")
    print("Eg: " + sys.argv[0] + " 48.87814394530428,2.2821558610475257,48.86862582223842,2.3059560444047054")
    print("The created map is called \"mapgen\"")
    sys.exit(0)

print("Work path:", config.data["work_path"])

if "export_path" in config.data:
    gvar.EXPORT_PATH = config.data["export_path"]
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
bbox.coordXY = {"north": helper.lat_to_x(north), "south": helper.lat_to_x(south), "west": helper.lon_to_y(west),
                "east": helper.lon_to_y(east)}
print("Bounding box:", bbox.coord)

osm_data = osm.get_data()

ror_zip_file.create_default_file()
ror_zip_file.write_default_file()

osm.dump_result_to_file(osm_data)

nodes_original = copy.deepcopy(osm_data.nodes)
ways_original = copy.deepcopy(osm_data.ways)
relations_original = copy.deepcopy(osm_data.relations)

osm_tags.filter_ignored(osm_data.nodes)
osm_tags.filter_ignored(osm_data.ways)
osm_tags.filter_ignored(osm_data.relations)

gen_sea.process(osm_data)

node_total = len(osm_data.nodes)
node_qty = 0
for node in osm_data.nodes:
    node_qty += 1
    if node_qty % 100 == 0:
        print("nodes: ", node_qty, "/", node_total, "\r", end="")

    if len(node.tags) == 0:
        continue
    gen_object.process(node)
print("nodes: ", node_qty, "/", node_total)

rel_total = len(osm_data.relations)
rel_qty = 0
for rel in osm_data.relations:
    rel_qty += 1
    if rel_qty % 10 == 0:
        print("relations: ", rel_qty, "/", rel_total, "\r", end="")

    if len(rel.tags) == 0:
        continue

    if gen_building.process(rel, osm_data):
        continue
    if gen_shelter.process(rel, osm_data):
        continue
    if gen_land.process(rel, osm_data):
        continue
    if gen_water.process(rel, osm_data):
        continue
print("relations: ", rel_qty, "/", rel_total)

way_total = len(osm_data.ways)
way_qty = 0
for way in osm_data.ways:
    way_qty += 1
    if way_qty % 10 == 0:
        print("ways: ", way_qty, "/", way_total, "\r", end="")

    if len(way.tags) == 0:
        continue

    if gen_building.process(way):
        continue
    if gen_shelter.process(way):
        continue
    if gen_land.process(way):
        continue
    if gen_water.process(way):
        continue

    if gen_barrier.process(way):
        continue
    if gen_road.process(way):
        continue
print("ways: ", way_qty, "/", way_total)

ror_zip_file.add_file(config.data["map_name"] + ".tobj")
ogre_material.add_file()

osm_tags.show_stat("nodes", nodes_original, osm_data.nodes)
osm_tags.show_stat("ways", ways_original, osm_data.ways)
osm_tags.show_stat("relations", relations_original, osm_data.relations)
