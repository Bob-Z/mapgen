import overpy
import gvar
import sys
import bbox
import time
import os
import pickle
import config
import math


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
    try:
        return osm_data.get_way(way_id)
    except overpy.exception.DataIncomplete:
        return None


def get_height(entity):
    height = None

    if "building:levels" in entity.tags:
        level_qty = entity.tags["building:levels"]
        try:
            height = float(level_qty) * config.data["building_level_height"]
            entity.tags.pop("building:levels")
        except ValueError:
            print("Cannot convert building:levels : " + entity.tags["building:levels"])

    if "height" in entity.tags:
        h = convert_height_to_meter(entity.tags["height"])
        if h is not None:
            height = h
            entity.tags.pop("height")

    roof_height = None
    if "roof:height" in entity.tags:
        h = convert_height_to_meter(entity.tags["roof:height"])
        if h is not None:
            roof_height = h
            entity.tags.pop("roof:height")
    if roof_height is None and "est_roof:height" in entity.tags:
        h = convert_height_to_meter(entity.tags["est_roof:height"])
        if h is not None:
            roof_height = h
            entity.tags.pop("est_roof:height")
    if roof_height is None and "roof:levels" in entity.tags:
        roof_height = float(entity.tags["roof:levels"]) * config.data["roof_height"]
        entity.tags.pop("roof:levels")

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

    # height = facade height + roof_height
    return height, min_height, roof_height


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


# all_way is a list of ways. This function returns a single way which is the concatenation of all way sorted by distance between input ways
def concat_way_by_distance(all_way):
    ready_nodes = all_way.pop()

    # Link roads with the same name
    while len(all_way) > 0:
        index = 0
        selected_index = 0
        distance = 999999.0
        for node in all_way:
            existing_first_point = [ready_nodes[0].lon, ready_nodes[0].lat]
            existing_last_point = [ready_nodes[-1].lon, ready_nodes[-1].lat]
            new_first_point = [node[0].lon, node[0].lat]
            new_last_point = [node[-1].lon, node[-1].lat]

            first_to_first_dist = math.dist(existing_first_point, new_first_point)
            first_to_last_dist = math.dist(existing_first_point, new_last_point)
            last_to_first_dist = math.dist(existing_last_point, new_first_point)
            last_to_last_dist = math.dist(existing_last_point, new_last_point)

            # Reverse node list if needed, depending on first and last vertices of each road
            if first_to_first_dist < first_to_last_dist and first_to_first_dist < last_to_first_dist and first_to_first_dist < last_to_last_dist:
                if first_to_first_dist < distance:
                    selected_index = index
                    distance = first_to_first_dist
                    ready_nodes.reverse()
            elif first_to_last_dist < first_to_first_dist and first_to_last_dist < last_to_first_dist and first_to_last_dist < last_to_last_dist:
                if first_to_last_dist < distance:
                    selected_index = index
                    distance = first_to_last_dist
                    ready_nodes.reverse()
                    node.reverse()
            elif last_to_first_dist < first_to_first_dist and last_to_first_dist < first_to_last_dist and last_to_first_dist < last_to_last_dist:
                if last_to_first_dist < distance:
                    selected_index = index
                    distance = last_to_first_dist
            elif last_to_last_dist < first_to_first_dist and last_to_last_dist < first_to_last_dist and last_to_last_dist < last_to_first_dist:
                if last_to_last_dist < distance:
                    selected_index = index
                    distance = last_to_last_dist
                    node.reverse()

            index += 1

        ready_nodes = ready_nodes + all_way.pop(selected_index)

    return ready_nodes
