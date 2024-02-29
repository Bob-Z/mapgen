import overpy

import gvar
import sys
import bbox
import time
import os
import pickle
import config


def get_data():
    bounding_box = str(bbox.coord["south"]) + "," + str(bbox.coord["west"]) + "," + str(
        bbox.coord["north"]) + "," + str(bbox.coord["east"])

    cache_file_path = config.data["cache_path"] + "/" + bounding_box
    if os.path.isfile(cache_file_path):
        print("Reading OpenStreetMap cache file\n")
        with open(cache_file_path, 'rb') as file:
            result = pickle.load(file)
    else:
        print("Requesting OpenStreetMap")
        start_time = time.time()
        overpy_api = overpy.Overpass()
        result = overpy_api.query(
            "(>>;node(" + bounding_box + ");>>;way(" + bounding_box + ");>>;rel(" + bounding_box + "););out;")
        end_time = time.time()

        print("Done in " + str(end_time - start_time) + " seconds\n")

        print("Writing OpenStreetMap cache file\n")
        with open(cache_file_path, 'wb') as file:
            pickle.dump(result, file)

    if has_tag(result, "natural", "coastline") is True:
        print("This is a water map\n")
        gvar.is_water_map = True

    return result


def dump_result_to_file(result):
    original_stdout = sys.stdout

    print("Dumping OSM data in " + config.data["log_path"] + "osm_request.txt")
    with open(config.data["log_path"] + "osm_request.txt", "w") as result_file:
        sys.stdout = result_file

        for node in result.nodes:
            print(node.tags, node)

        for way in result.ways:
            print(way.tags, way)

        for relation in result.relations:
            print(relation, relation.tags)
            for member in relation.members:
                print(member)

    sys.stdout = original_stdout


def has_tag(result, tag, value):
    for node in result.nodes:
        if tag in node.tags:
            if node.tags[tag] == value:
                return True

    for way in result.ways:
        if tag in way.tags:
            if way.tags[tag] == value:
                return True

    for relation in result.relations:
        if tag in relation.tags:
            if relation.tags[tag] == value:
                return True

    return False


def get_way_by_id(osm_data, way_id):
    for way in osm_data.ways:
        if way.id == way_id:
            return way


def get_height(entity):
    height = None

    if "building:levels" in entity.tags:
        level_qty = entity.tags["building:levels"]
        try:
            height = float(level_qty) * config.data["building_level_height"]
            entity.tags.pop("building:levels")
        except ValueError:
            print("Cannot convert building:levels : " + entity.tags["building:levels"])

    h = None
    if "height" in entity.tags:
        h = convert_height_to_meter(entity.tags["height"])
        if h is not None:
            height = h
            entity.tags.pop("height")

    if h is None and "est_roof:height" in entity.tags:
        h = convert_height_to_meter(entity.tags["est_roof:height"])
        if h is not None:
            height = h
            entity.tags.pop("est_roof:height")

    min_height = None
    if "min_height" in entity.tags:
        height, min_height = get_min_height(height, convert_height_to_meter(entity.tags["min_height"]))
        if min_height is not None:
            entity.tags.pop("min_height")
    elif "building:min_level" in entity.tags:
        level_qty = entity.tags["building:min_level"]
        min_h = None
        try:
            min_h = float(level_qty) * config.data["building_level_height"]
        except ValueError:
            print("Cannot convert building:levels : " + entity.tags["building:min_level"])

        height, min_height = get_min_height(height, min_h)
        if min_height is not None:
            entity.tags.pop("building:min_level")

    return height, min_height


def get_min_height(height, min_height):
    if min_height is not None:
        if height is None:
            height = config.data["building_level_height"]
        else:
            height = height - min_height

    return height, min_height


def convert_height_to_meter(height):
    height_in_meter = None

    convert_rate = 1.0
    height = height.replace(' m', '')  # Some height appear like: 100 m
    if height.find(" ft") != -1:
        height = height.replace(' ft', '')
        convert_rate = 0.3048
    if height.find(" storey") != -1:
        height = height.replace(' storey', '')
        convert_rate = config.data["building_level_height"]

    try:
        height_in_meter = float(height) * convert_rate
    except ValueError:
        print("Cannot convert height: " + height)

    return height_in_meter
