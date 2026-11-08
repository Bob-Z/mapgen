import sys
import bbox
import time
import os
import pickle
import config
import math
import requests

elements = {}

def get_data():
    global elements

    bounding_box = str(bbox.coord["south"]) + "," + str(bbox.coord["west"]) + "," + str(
        bbox.coord["north"]) + "," + str(bbox.coord["east"])

    cache_file_path = config.data["cache_path"] + "/" + bounding_box
    if os.path.isfile(cache_file_path):
        print("Reading OpenStreetMap cache file " + cache_file_path + "\n")
        with open(cache_file_path, 'rb') as file:
            elements = pickle.load(file)
    else:
        print("Requesting OpenStreetMap overall data")
        print("Chunk quantity is", config.data["osm_chunk_qty"], ".")

        bounding_box = []

        dist_x = (bbox.coord["west"] - bbox.coord["east"]) / config.data["osm_chunk_qty"]
        dist_y = (bbox.coord["south"] - bbox.coord["north"]) / config.data["osm_chunk_qty"]
        for x in range(config.data["osm_chunk_qty"]):
            for y in range(config.data["osm_chunk_qty"]):
                bounding_box.append(str(bbox.coord["south"] - (dist_y * y)) + "," + str(
                    bbox.coord["west"] - (dist_x * x)) + "," + str(
                    bbox.coord["south"] - (dist_y * (y + 1))) + "," + str(bbox.coord["west"] - (dist_x * (x + 1))))

        query_list = []
        chunk_index = 1
        # for box in bounding_box:
        #    print("Get chunk ", chunk_index, "/", len(bounding_box))
        #    query_list.append(query_openstreetmap(
        # "(>>;node(" + bounding_box + ");>>;way(" + bounding_box + ");>>;rel(" + bounding_box + ");>>;nwr(" + bounding_box + "););"
        # "(node(" + bounding_box + ");>>;way(" + bounding_box + ");>>;rel(" + bounding_box + ");>>;nwr(" + bounding_box + "););"
        # "(nwr(" + box + ");<;>;);"
        #        "nwr(" + box + ");>>;"
        #    ))
        #    chunk_index += 1

        overall_data = query_openstreetmap(
            # "(>>;node(" + bounding_box + ");>>;way(" + bounding_box + ");>>;rel(" + bounding_box + ");>>;nwr(" + bounding_box + "););"
            # "(node(" + bounding_box + ");>>;way(" + bounding_box + ");>>;rel(" + bounding_box + ");>>;nwr(" + bounding_box + "););"
            # "(nwr(" + box + ");<;>;);"
            "nwr(" + bounding_box[0] + ");>>;"
        )
        # for q in query_list:
        #    overall_data = overall_data + q

        # FIXME: Find the right query to have both coastlines and all other data in one request
        # print("Requesting OpenStreetMap coastlines")
        # coastline_data = query(
        # "node(" + max_bounding_box + ");<;>;")
        #    "nwr[\"natural\"=\"coastline\"](" + max_bounding_box + ");<;>;")

        # respond = {"features": overall_data["features"] + coastline_data["features"]}
        elements = {"nodes": [], "ways": [], "relations": []}

        for element in overall_data["elements"]:
            if element["type"] == "node":
                if "tags" not in element:
                    element["tags"] = {}
                elements["nodes"].append(element)
            elif element["type"] == "way":
                if "tags" not in element:
                    element["tags"] = {}
                nodes_value = []
                for node in element["nodes"]:
                    nodes_value.append(get_node_by_id(node))
                element["nodes"] = nodes_value
                elements["ways"].append(element)
            if element["type"] == "relation":
                if "tags" not in element:
                    element["tags"] = {}
                elements["relations"].append(element)

        print("Writing OpenStreetMap cache file " + cache_file_path + "\n")
        with open(cache_file_path, 'wb') as file:
            pickle.dump(elements, file)

    if has_tag(elements, "natural", "coastline") is True:
        print("This is a water map\n")

    return elements


def dump_result_to_file(elements):
    original_stdout = sys.stdout

    print("Dumping OSM data in " + config.data["log_path"] + "osm_request.txt")
    with open(config.data["log_path"] + "osm_request.txt", "w") as result_file:
        sys.stdout = result_file

        for node in elements["nodes"]:
            print(node)

        for way in elements["ways"]:
            print(way)

        for relation in elements["relations"]:
            print(relation)
            for member in relation["members"]:
                print(member)

    sys.stdout = original_stdout


def has_tag(elements, tag, value):
    for node in elements["nodes"]:
        if tag in node["tags"]:
            if node["tags"][tag] == value:
                return True

    for way in elements["ways"]:
        if tag in way["tags"]:
            if way["tags"][tag] == value:
                return True

    for relation in elements["relations"]:
        if tag in relation["tags"]:
            if relation["tags"][tag] == value:
                return True

    return False


def get_node_by_id(node_id):
    return next((item for item in elements["nodes"] if item["id"] == node_id), None)


def get_way_by_id(way_id):
    return next((item for item in elements["ways"] if item["id"] == way_id), None)


def get_height(entity):
    height = None

    if "building:levels" in entity["tags"]:
        level_qty = entity["tags"]["building:levels"]
        try:
            height = float(level_qty) * config.data["building_level_height"]
            entity["tags"].pop("building:levels")
        except ValueError:
            print("Cannot convert building:levels : " + entity["tags"]["building:levels"])

    if "height" in entity["tags"]:
        h = convert_height_to_meter(entity["tags"]["height"])
        if h is not None:
            height = h
            entity["tags"].pop("height")

    roof_height = None
    if "roof:height" in entity["tags"]:
        h = convert_height_to_meter(entity["tags"]["roof:height"])
        if h is not None:
            roof_height = h
            entity["tags"].pop("roof:height")
    if roof_height is None and "est_roof:height" in entity["tags"]:
        h = convert_height_to_meter(entity["tags"]["est_roof:height"])
        if h is not None:
            roof_height = h
            entity["tags"].pop("est_roof:height")
    if roof_height is None and "roof:levels" in entity["tags"]:
        try:
            roof_height = float(entity["tags"]["roof:levels"]) * config.data["roof_height"]
            entity["tags"].pop("roof:levels")
        except ValueError:
            print("Cannot convert roof:levels : " + entity["tags"]["roof:levels"])

    min_height = None
    if "min_height" in entity["tags"]:
        height, min_height = get_min_height(height, convert_height_to_meter(entity["tags"]["min_height"]))
        if min_height is not None:
            entity["tags"].pop("min_height")
    elif "building:min_level" in entity["tags"]:
        level_qty = entity["tags"]["building:min_level"]
        min_h = None
        try:
            min_h = float(level_qty) * config.data["building_level_height"]
        except ValueError:
            print("Cannot convert building:levels : " + entity["tags"]["building:min_level"])

        height, min_height = get_min_height(height, min_h)
        if min_height is not None:
            entity["tags"].pop("building:min_level")

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
    elif height.find("'") != -1:
        height = height.replace('\'', '')
        convert_rate = 0.3048
    elif height.find(",") != -1:
        height = height.replace(',', '.')
    elif height.find(" storey") != -1:
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
            existing_first_point = [ready_nodes[0]["lon"], ready_nodes[0]["lat"]]
            existing_last_point = [ready_nodes[-1]["lon"], ready_nodes[-1]["lat"]]
            new_first_point = [node[0]["lon"], node[0]["lat"]]
            new_last_point = [node[-1]["lon"], node[-1]["lat"]]

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


def query_openstreetmap(query):
    # Overpass API endpoint
    overpass_url = "http://overpass-api.de/api/interpreter"

    # Define the Overpass QL query
    # This example searches for nodes tagged with 'amenity=cafe'
    # inside a specified bounding box (min_lat, min_lon, max_lat, max_lon)
    # Example bounding box: central Paris
    # [out:json][maxsize:1073741824];
    overpass_query = """
    [out:json];
    (""" + query + """
    );
    out body;
    """

    print("Sending request to Overpass API...")

    # Send the POST request with the query
    headers = {
        'User-Agent': 'mapgen',
    }

    data = None
    while data is None:
        start_time = time.time()
        response = requests.post(overpass_url, data={"data": overpass_query}, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            end_time = time.time()
            data = response.json()
            print(f"Success! Found {len(data.get('elements', []))} elements in {str(end_time - start_time)} seconds\n")
            return data
        elif response.status_code == 502:
            wait_time = 5.0
        else:
            wait_time = 2.0

        print(
            f"Error: Received status code {response.status_code}"
            f" - {response.text}"
            f"Waiting for {wait_time} seconds"
        )
        time.sleep(wait_time)

        print("Retrying")
    return None
