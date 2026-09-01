import overpass
import sys
import bbox
import time
import os
import pickle
import config
import math
import urllib
import http


def get_data():
    bounding_box = str(bbox.coord["south"]) + "," + str(bbox.coord["west"]) + "," + str(
        bbox.coord["north"]) + "," + str(bbox.coord["east"])

    cache_file_path = config.data["cache_path"] + "/" + bounding_box + "," + str(config.data["map_size"])
    if os.path.isfile(cache_file_path):
        print("Reading OpenStreetMap cache file " + cache_file_path + "\n")
        with open(cache_file_path, 'rb') as file:
            respond = pickle.load(file)
    else:
        print("Requesting OpenStreetMap")

        start_time = time.time()
        overpy_api = overpass.API(user_agent="mapgen")

        respond = None
        while respond is None:
            try:
                respond = overpy_api.get(
                    #"(>>;node(" + bounding_box + ");>>;way(" + bounding_box + ");>>;rel(" + bounding_box + "););out;"
                    "(>>;node(" + bounding_box + ");>>;way(" + bounding_box + ");>>;rel(" + bounding_box + ");>>;nwr(" + bounding_box + "););out;"
                    #"(>>;nwr(" + bounding_box + "););out;"
                )
            except overpass.ServerLoadError as e:
                print("OSM server is under load. Waiting 5 seconds")
                time.sleep(5.0)
                print("Retrying")
            except urllib.error.URLError as e:
                print("OSM server error: ", e)
                return None
            except http.client.RemoteDisconnected as e:
                print("OSM server error: ", e)
                return None

        end_time = time.time()

        print("Done in " + str(end_time - start_time) + " seconds\n")

        print("Writing OpenStreetMap cache file " + cache_file_path + "\n")
        with open(cache_file_path, 'wb') as file:
            pickle.dump(respond, file)

    if has_tag(respond, "natural", "coastline") is True:
        print("This is a water map\n")

    return respond


def dump_result_to_file(respond):
    original_stdout = sys.stdout

    print("Dumping OSM data in " + config.data["log_path"] + "osm_request.txt")
    with open(config.data["log_path"] + "osm_request.txt", "w") as result_file:
        sys.stdout = result_file

        print(respond)

    with open(config.data["log_path"] + "osm_request_nodes.txt", "w") as result_file:
        sys.stdout = result_file

        for feature in respond["features"]:
            if "type" in feature["properties"] and feature["properties"]["type"] == "node":
                print(feature)

    with open(config.data["log_path"] + "osm_request_ways.txt", "w") as result_file:
        sys.stdout = result_file

        for feature in respond["features"]:
            if "type" in feature["properties"] and feature["properties"]["type"] == "way":
                print(feature)

    with open(config.data["log_path"] + "osm_request_relations.txt", "w") as result_file:
        sys.stdout = result_file

        for feature in respond["features"]:
            if "type" in feature["properties"] and feature["properties"]["type"] == "relation":
                print(feature)

    with open(config.data["log_path"] + "osm_request_other.txt", "w") as result_file:
        sys.stdout = result_file

        for feature in respond["features"]:
            if "type" in feature["properties"] and feature["properties"]["type"] != "relation" and \
                    feature["properties"]["type"] != "way" and feature["properties"]["type"] != "node":
                print(feature)

    sys.stdout = original_stdout


def has_tag(result, tag, value):
    for feature in result["features"]:
        if "tags" in feature["properties"]:
            if tag in feature["properties"]["tags"]:
                if feature["properties"]["tags"][tag] == value:
                    return True

    return False


def get_way_by_id(osm_data, way_id):
    try:
        return osm_data.get_way(way_id)
    except overpy.exception.DataIncomplete:
        return None


def get_height(feature):
    height = None

    tags = feature["properties"]["tags"]

    if "building:levels" in tags:
        level_qty = tags["building:levels"]
        try:
            height = float(level_qty) * config.data["building_level_height"]
            tags.pop("building:levels")
        except ValueError:
            print("Cannot convert building:levels : " + tags["building:levels"])

    if "height" in tags:
        h = convert_height_to_meter(tags["height"])
        if h is not None:
            height = h
            tags.pop("height")

    roof_height = None
    if "roof:height" in tags:
        h = convert_height_to_meter(tags["roof:height"])
        if h is not None:
            roof_height = h
            tags.pop("roof:height")
    if roof_height is None and "est_roof:height" in tags:
        h = convert_height_to_meter(tags["est_roof:height"])
        if h is not None:
            roof_height = h
            tags.pop("est_roof:height")
    if roof_height is None and "roof:levels" in tags:
        roof_height = float(tags["roof:levels"]) * config.data["roof_height"]
        tags.pop("roof:levels")

    min_height = None
    if "min_height" in tags:
        height, min_height = get_min_height(height, convert_height_to_meter(tags["min_height"]))
        if min_height is not None:
            tags.pop("min_height")
    elif "building:min_level" in tags:
        level_qty = tags["building:min_level"]
        min_h = None
        try:
            min_h = float(level_qty) * config.data["building_level_height"]
        except ValueError:
            print("Cannot convert building:levels : " + tags["building:min_level"])

        height, min_height = get_min_height(height, min_h)
        if min_height is not None:
            tags.pop("building:min_level")

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


# all_all_cord is a list of all_cord. all_cord is list of coord. This function returns a single way which is the concatenation of all way sorted by distance between input ways
def concat_way_by_distance(all_all_cord):
    ready_coord = all_all_cord.pop()

    # Link roads with the same name
    while len(all_all_cord) > 0:
        index = 0
        selected_index = 0
        distance = 999999.0
        for all_cord in all_all_cord:
            existing_first_point = [ready_coord[0][0], ready_coord[0][1]]
            existing_last_point = [ready_coord[-1][0], ready_coord[-1][1]]
            new_first_point = [all_cord[0][0], all_cord[0][1]]
            new_last_point = [all_cord[-1][0], all_cord[-1][1]]

            first_to_first_dist = math.dist(existing_first_point, new_first_point)
            first_to_last_dist = math.dist(existing_first_point, new_last_point)
            last_to_first_dist = math.dist(existing_last_point, new_first_point)
            last_to_last_dist = math.dist(existing_last_point, new_last_point)

            # Reverse node list if needed, depending on first and last vertices of each road
            if first_to_first_dist < first_to_last_dist and first_to_first_dist < last_to_first_dist and first_to_first_dist < last_to_last_dist:
                if first_to_first_dist < distance:
                    selected_index = index
                    distance = first_to_first_dist
                    ready_coord.reverse()
            elif first_to_last_dist < first_to_first_dist and first_to_last_dist < last_to_first_dist and first_to_last_dist < last_to_last_dist:
                if first_to_last_dist < distance:
                    selected_index = index
                    distance = first_to_last_dist
                    ready_coord.reverse()
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

        ready_coord = ready_coord + all_all_cord.pop(selected_index)

    return ready_coord


# return an array of array of coord i.e. [lon,lat]
def get_coord_from_feature(feature):
    all_all_coord = []

    if feature["geometry"]["type"] == "MultiPolygon":
        for all_cord in feature["geometry"]["coordinates"][0]:
            all_all_coord.append(all_cord)
    elif feature["geometry"]["type"] == "Polygon":
        all_all_coord = [feature["geometry"]["coordinates"][0]]
    elif feature["geometry"]["type"] == "LineString":
        all_all_coord = [feature["geometry"]["coordinates"]]
    elif feature["geometry"]["type"] == "MultiLineString":
        all_all_coord = feature["geometry"]["coordinates"]
    else:
        print("Unsupported geometry " + feature["geometry"]["type"])
        sys.exit(-1)

    return all_all_coord
