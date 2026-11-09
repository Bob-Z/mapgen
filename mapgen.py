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
from multiprocessing import Process, freeze_support, set_start_method


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

    bbox.init(center_coord, config.data["map_size"])

    print("Work path:", config.data["work_path"])
    print("Export path:", config.data["export_path"])
    print("")

    wiki.init()

    topography.get(api_key)

    elements = osm.get_data()

    ror_zip_file.create_default_file(api_key)

    json_string = json.dumps(config.data, indent=2)
    with open(config.data["work_path"] + "config.json", "w") as json_file:
        json_file.write(json_string)
    ror_zip_file.add_to_zip_file_list("config.json")

    if config.data["generate_statistics"] is True:
        nodes_original = copy.deepcopy(elements["nodes"])
        ways_original = copy.deepcopy(elements["ways"])
        relations_original = copy.deepcopy(elements["relations"])

    osm_tags.filter_ignored(elements["nodes"])
    osm_tags.filter_ignored(elements["ways"])
    osm_tags.filter_ignored(elements["relations"])

    gen_sea.process(elements)

    if config.data["use_wikidata"] is True:
        print("Searching for 3D model in OSM data...")
        for rel in elements["relations"]:
            wiki.get_data(rel)
        for way in elements["ways"]:
            wiki.get_data(way)

    print("Processing nodes...")
    node_total = len(elements["nodes"])
    node_qty = 0
    for node in elements["nodes"]:
        node_qty += 1
        if node_qty % 100 == 0:
            print("nodes: ", node_qty, "/", node_total, "\r", end="")

        if len(node["tags"]) == 0:
            continue

        if osm_tags.is_entity_ignored(node):
            continue

        gen_object.process(node)
    print("nodes: ", node_qty, "/", node_total)

    print("Processing relations...")
    rel_total = len(elements["relations"])
    rel_qty = 0
    for rel in elements["relations"]:
        rel_qty += 1
        if rel_qty % 10 == 0:
            print("first pass relations: ", rel_qty, "/", rel_total, "\r", end="")

        if len(rel["tags"]) == 0:
            continue

        if osm_tags.is_entity_ignored(rel):
            continue

        if gen_building.process(rel, elements, pass_index=0):
            continue
        if gen_shelter.process(rel, elements):
            continue
        if gen_land.process(rel, elements):
            continue
        if gen_water.process(rel, elements):
            continue
        if gen_road.process(rel, elements):
            continue

    # Second pass
    rel_total = len(elements["relations"])
    rel_qty = 0
    for rel in elements["relations"]:
        rel_qty += 1
        if rel_qty % 10 == 0:
            print("second pass relations: ", rel_qty, "/", rel_total, "\r", end="")

        if len(rel["tags"]) == 0:
            continue

        if osm_tags.is_entity_ignored(rel):
            continue

        if gen_building.process(rel, elements, pass_index=1):
            continue

    print("relations: ", rel_qty, "/", rel_total)

    print("Processing ways...")
    # First pass
    way_total = len(elements["ways"])
    way_qty = 0
    for way in elements["ways"]:
        way_qty += 1
        if way_qty % 10 == 0:
            print("first pass ways: ", way_qty, "/", way_total, "\r", end="")

        if len(way["tags"]) == 0:
            continue

        if osm_tags.is_entity_ignored(way):
            continue

        if gen_building.process(way, pass_index=0):
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

    # second pass
    way_total = len(elements["ways"])
    way_qty = 0
    for way in elements["ways"]:
        way_qty += 1
        if way_qty % 10 == 0:
            print("second pass ways: ", way_qty, "/", way_total, "\r", end="")

        if len(way["tags"]) == 0:
            continue

        if osm_tags.is_entity_ignored(way):
            continue

        if gen_building.process(way, pass_index=1):
            continue

    print("ways: ", way_qty, "/", way_total)
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
    ogre_map_vegetation.create_file(gen_road.get_road_coord())  # must be called after gen_road.write_all_roads()

    ror_zip_file.write_default_file()
    ror_zip_file.create_zip_file()

    if config.data["generate_statistics"] is True:
        osm_tags.show_stat("nodes", nodes_original, elements["nodes"])
        osm_tags.show_stat("ways", ways_original, elements["ways"])
        osm_tags.show_stat("relations", relations_original, elements["relations"])


if __name__ == '__main__':
    # freeze_support()
    # set_start_method('spawn')
    # p = Process(target=my_main)
    # p.start()
    my_main()
