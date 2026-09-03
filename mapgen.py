import time

import ror_as_script
import config
import helper
import ogre_map_vegetation
import ror_waypoint_file
import ror_zip_file
import osm
import topography
import bbox
import sys
import ogre_material
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
import ror_terrn2_file
import ror_as_file
import json
import wiki
import os
from multiprocessing import Process,freeze_support,set_start_method

def my_main():
    try:
        os.mkdir(config.data["cache_path"])
    except OSError as e:
        if e.errno != 17:
            raise e
    try:
        os.mkdir(config.data["work_path"])
    except OSError as e:
        if e.errno != 17:
            raise e

    skip_first = True
    for arg in sys.argv:
        if skip_first:
            skip_first = False
            continue
        param = arg.split('=')
        if param[0] not in config.data:
            print("Unknown parameter:", param[0])
            sys.exit(0)
        print("Parameter", param[0], "set to", param[1])
        if type(config.data[param[0]]) is bool:
            if param[1].lower() in ['true', '1', 't', 'y', 'yes']:
                param[1] = True
            else:
                param[1] = False
        elif type(config.data[param[0]]) is float:
            param[1] = float(param[1])
        elif type(config.data[param[0]]) is int:
            param[1] = int(param[1])

        config.data[param[0]] = param[1]
    print("")

    center_coord = config.data["coord"].split(',')
    print("Coordinates:", center_coord)

    if helper.is_power_of_2(config.data["map_size"]) is False:
        print("Given map size is " + str(config.data["map_size"]) + ", but map size must be a power of 2")
        sys.exit(0)
    print("Map size:", config.data["map_size"], "meters")

    if helper.is_power_of_2(config.data["map_precision"]) is False:
        print("Map precision must be a power of 2")
        sys.exit(0)
    print("Map precision:", config.data["map_precision"], "meters")

    api_key = config.data["api_key"]
    # Avoid record API key in config.json
    config.data["api_key"] = ""

    center_lat = float(center_coord[0])
    center_lon = float(center_coord[1])
    meter_by_decimal_latitude = helper.lat_lon_to_distance(center_lat, center_lat + 0.1, center_lon, center_lon)
    meter_by_decimal_longitude = helper.lat_lon_to_distance(center_lat, center_lat, center_lon, center_lon + 0.1)

    north = center_lat + (config.data["map_size"] / 2.0) / meter_by_decimal_latitude * 0.1
    south = center_lat - (config.data["map_size"] / 2.0) / meter_by_decimal_latitude * 0.1
    west = center_lon + (config.data["map_size"] / 2.0) / meter_by_decimal_longitude * 0.1
    east = center_lon - (config.data["map_size"] / 2.0) / meter_by_decimal_longitude * 0.1

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
    # print("Bounding box:", bbox.coord, bbox.coordXY)

    print("Work path:", config.data["work_path"])
    print("Export path:", config.data["export_path"])
    print("")

    wiki.init()

    topography.get(api_key)

    osm_data = None

    retry_timeout = 30.0

    while osm_data is None:
        osm_data = osm.get_data()
        if osm_data is None:
            print("Can't download OSM data. Waiting for " + str(retry_timeout) + " seconds before retry. You may also try a smaller map.")
            time.sleep(retry_timeout)

    ror_zip_file.create_default_file()

    osm.dump_result_to_file(osm_data)

    json_string = json.dumps(config.data, indent=2)
    with open(config.data["work_path"] + "config.json", "w") as json_file:
        json_file.write(json_string)
    ror_zip_file.add_to_zip_file_list("config.json")

    if config.data["generate_statistics"] is True:
        nodes_original = copy.deepcopy(osm_data.nodes)
        ways_original = copy.deepcopy(osm_data.ways)
        relations_original = copy.deepcopy(osm_data.relations)

    osm_tags.filter_ignored(osm_data)

    gen_sea.process(osm_data)

    if config.data["use_wikidata"] is True:
        print("Searching for 3D model in OSM data...")
        wiki.get_data(osm_data)

    print("Processing nodes...")
    node_id = []
    node_total = 0
    node_duplicate = 0
    for feature in osm_data["features"]:
        if feature["properties"]["type"] == "node":
            node_total += 1
            if feature["properties"]["id"] not in node_id:
                node_id.append(feature["properties"]["id"])
            else:
                node_duplicate += 1
    node_id = []
    node_qty = 0
    for feature in osm_data["features"]:
        if feature["properties"]["type"] == "node":
            if feature["properties"]["id"] not in node_id:
                node_qty += 1
                node_id.append(feature["properties"]["id"])
                if node_qty % 100 == 0:
                    print("nodes: ", node_qty, "/", node_total, "\r", end="")

                if len(feature["properties"]["tags"]) == 0:
                    continue

                if osm_tags.is_entity_ignored(feature["properties"]["tags"]):
                    continue

                gen_object.process(feature)
    print("nodes: ", node_qty, "/", node_total, " (duplicate ", node_duplicate,")")

    print("Processing relations...")
    rel_id = []
    rel_duplicate = 0
    rel_total = 0
    for feature in osm_data["features"]:
        if feature["properties"]["type"] == "relation":
            rel_total += 1
            if feature["properties"]["id"] not in rel_id:
                rel_id.append(feature["properties"]["id"])
            else:
                rel_duplicate += 1

    rel_id = []
    rel_qty = 0
    for feature in osm_data["features"]:
        if feature["properties"]["type"] == "relation":
            if feature["properties"]["id"] not in rel_id:
                rel_qty += 1
                rel_id.append(feature["properties"]["id"])

                if rel_qty % 10 == 0:
                    print("first pass relations: ", rel_qty, "/", rel_total, "\r", end="")

                if len(feature["properties"]["tags"]) == 0:
                    continue

                if osm_tags.is_entity_ignored(feature["properties"]["tags"]):
                    continue

                if gen_building.process(feature, osm_data, pass_index=0):
                    continue
                if gen_shelter.process(feature, osm_data):
                    continue
                if gen_land.process(feature):
                    continue
                if gen_water.process(feature):
                    continue
                if gen_road.process(feature, osm_data):
                    continue

    # Second pass
    rel_id = []
    rel_qty = 0
    for feature in osm_data["features"]:
        if feature["properties"]["type"] == "relation":
            if feature["properties"]["id"] not in rel_id:
                rel_id.append(feature["properties"]["id"])
                rel_qty += 1

                if rel_qty % 10 == 0:
                    print("second pass relations: ", rel_qty, "/", rel_total, "\r", end="")

                if len(feature["properties"]["tags"]) == 0:
                    continue

                if osm_tags.is_entity_ignored(feature["properties"]["tags"]):
                    continue

                if gen_building.process(feature, osm_data, pass_index=1):
                    continue

    print("relations: ", rel_qty, "/", rel_total, " (duplicate ", rel_duplicate,")")

    print("Processing ways...")
    # First pass
    way_id = []
    way_total = 0
    way_duplicate = 0

    for feature in osm_data["features"]:
        if feature["properties"]["type"] == "way":
            way_total += 1
            if feature["properties"]["id"] not in way_id:
                way_id.append(feature["properties"]["id"])
            else:
                way_duplicate += 1

    way_id = []
    way_qty = 0
    for feature in osm_data["features"]:
        if feature["properties"]["type"] == "way":
            if feature["properties"]["id"] not in way_id:
                way_id.append(feature["properties"]["id"])
                way_qty += 1

                if way_qty % 10 == 0:
                    print("first pass ways: ", way_qty, "/", way_total, "\r", end="")

                if len(feature["properties"]["tags"]) == 0:
                    continue

                if osm_tags.is_entity_ignored(feature):
                    continue

                if gen_building.process(feature, pass_index=0):
                    continue
                if gen_shelter.process(feature):
                    continue
                if gen_land.process(feature):
                    continue
                if gen_water.process(feature):
                    continue
                if gen_barrier.process(feature):
                    continue
                if gen_road.process(feature):
                    continue

    # second pass
    way_id = []
    way_qty = 0
    for feature in osm_data["features"]:
        if feature["properties"]["type"] == "way":
            if feature["properties"]["id"] not in way_id:
                way_id.append(feature["properties"]["id"])
                way_qty += 1

                if way_qty % 10 == 0:
                    print("second pass ways: ", way_qty, "/", way_total, "\r", end="")

                if len(feature["properties"]["tags"]) == 0:
                    continue

                if osm_tags.is_entity_ignored(feature["properties"]["tags"]):
                    continue

                if gen_building.process(feature, pass_index=1):
                    continue

    print("ways: ", way_qty, "/", way_total, " (duplicate ", way_duplicate,")")
    print("")

    wiki.print_data()

    ror_terrn2_file.create_file()

    ror_zip_file.add_to_zip_file_list(config.data["map_name"] + ".tobj")
    ror_zip_file.add_to_zip_file_list(config.data["map_name"] + "_vegetation.tobj")

    gen_road.write_all_roads()
    ror_waypoint_file.write()
    ror_as_file.write()

    ogre_material.create_file()
    ogre_map_height.create_file()
    ogre_map_surface.create_file()
    ogre_map_vegetation.create_file(gen_road.get_road_coord()) # must be called after gen_road.write_all_roads()

    ror_zip_file.write_default_file()
    ror_zip_file.create_zip_file()

    if config.data["generate_statistics"] is True:
        osm_tags.show_stat("nodes", nodes_original, osm_data.nodes)
        osm_tags.show_stat("ways", ways_original, osm_data.ways)
        osm_tags.show_stat("relations", relations_original, osm_data.relations)

if __name__ == '__main__':
    #freeze_support()
    #set_start_method('spawn')
    #p = Process(target=my_main)
    #p.start()
    my_main()
