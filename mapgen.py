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
import ogre_map_height
import ogre_map_surface

if len(sys.argv) < 2 or len(sys.argv) > 3:
    print("\nUsage: " + sys.argv[0] + " <latitude, longitude> <map size>")
    print("<latitude, longitude> coordinate of the map center")
    print("<map size> Map is always square. This must be a power of 2. Default to 512 meters")
    print("Eg: " + sys.argv[0] + " 48.87814394530428,2.2821558610475257 1024")
    print("Default map name is \"mapgen\". This can be modified in config.json file.")
    sys.exit(0)

map_size = 512.0
if len(sys.argv) == 3:
    map_size = float(sys.argv[2])
    if helper.is_power_of_2(map_size) is False:
        print("Map size must be a power of 2")
        sys.exit(0)

center_coord = sys.argv[1].split(',')
center_lat = float(center_coord[0])
center_lon = float(center_coord[1])
meter_by_decimal_latitude = helper.lat_lon_to_distance(center_lat, center_lat + 0.1, center_lon, center_lon)
meter_by_decimal_longitude = helper.lat_lon_to_distance(center_lat, center_lat, center_lon, center_lon + 0.1)

north = center_lat + (map_size / 2.0) / meter_by_decimal_latitude * 0.1
south = center_lat - (map_size / 2.0) / meter_by_decimal_latitude * 0.1
west = center_lon + (map_size / 2.0) / meter_by_decimal_longitude * 0.1
east = center_lon - (map_size / 2.0) / meter_by_decimal_longitude * 0.1

if north < south:
    t = south
    south = north
    north = t
if west > east:
    t = west
    west = east
    east = t

bbox.coord = {"north": north, "south": south, "west": west, "east": east}
bbox.coordXY = {"north": helper.lat_to_y(north), "south": helper.lat_to_y(south), "west": helper.lon_to_x(west),
                "east": helper.lon_to_x(east)}
print("Bounding box:", bbox.coord)

print("Work path:", config.data["work_path"])

if "export_path" in config.data:
    gvar.EXPORT_PATH = config.data["export_path"]
print("Export path: ", gvar.EXPORT_PATH)

osm_data = osm.get_data()

ror_zip_file.create_default_file(map_size)
ror_zip_file.write_default_file()

osm.dump_result_to_file(osm_data)

if config.data["generate_statistics"] is True:
    nodes_original = copy.deepcopy(osm_data.nodes)
    ways_original = copy.deepcopy(osm_data.ways)
    relations_original = copy.deepcopy(osm_data.relations)

osm_tags.filter_ignored(osm_data.nodes)
osm_tags.filter_ignored(osm_data.ways)
osm_tags.filter_ignored(osm_data.relations)

gen_sea.process(osm_data)

print("Processing nodes...")
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

print("Processing relations...")
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

print("Processing ways...")
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

ror_zip_file.add_to_zip_file_list(config.data["map_name"] + ".tobj")

ogre_material.create_file()
ogre_map_height.create_file()
ogre_map_surface.create_file()

ror_zip_file.create_zip_file()

if config.data["generate_statistics"] is True:
    osm_tags.show_stat("nodes", nodes_original, osm_data.nodes)
    osm_tags.show_stat("ways", ways_original, osm_data.ways)
    osm_tags.show_stat("relations", relations_original, osm_data.relations)
