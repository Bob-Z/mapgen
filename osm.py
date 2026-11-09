import sys
import time
import bbox
import cache
import config
import math
import requests

elements = {}


def get_data():
    global elements

    elements = cache.load_osm_elements()

    if elements is None:
        print("Requesting OpenStreetMap elements")

        response = query_openstreetmap(
            "nwr(" + bbox.bounding_box + ");>>;"
        )

        prepare_elements(response)

        cache.save_osm_elements(elements)

    dump_result_to_file()

    return elements


def dump_result_to_file():
    original_stdout = sys.stdout

    print("Dumping OSM elements in " + config.data["log_path"])
    with open(config.data["log_path"] + "osm_elements.txt", "w") as result_file:
        sys.stdout = result_file
        for node in elements["nodes"]:
            print(node)
        for way in elements["ways"]:
            print(way)
        for relation in elements["relations"]:
            print(relation)
            for member in relation["members"]:
                print(member)

    with open(config.data["log_path"] + "osm_elements_nodes.txt", "w") as result_file:
        sys.stdout = result_file
        for node in elements["nodes"]:
            print(node)

    with open(config.data["log_path"] + "osm_elements_ways.txt", "w") as result_file:
        sys.stdout = result_file
        for way in elements["ways"]:
            print(way)

    with open(config.data["log_path"] + "osm_elements_relations.txt", "w") as result_file:
        sys.stdout = result_file
        for relation in elements["relations"]:
            print(relation)
            for member in relation["members"]:
                print(member)

    sys.stdout = original_stdout


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
    overpass_url = "http://overpass-api.de/api/interpreter"

    overpass_query = """
    [out:json];
    (""" + query + """
    );
    out body;
    """

    print("Sending request to Overpass API...")

    headers = {
        'User-Agent': 'mapgen',
    }

    data = None
    while data is None:
        start_time = time.time()
        response = requests.post(overpass_url, data={"data": overpass_query}, headers=headers)

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


def prepare_elements(response):
    global elements
    elements = {"nodes": [], "ways": [], "relations": []}

    nodes_by_id = {}

    for element in response["elements"]:
        if element["type"] == "node":
            if "tags" not in element:
                element["tags"] = {}
            elements["nodes"].append(element)
            nodes_by_id[element["id"]] = element
        elif element["type"] == "way":
            if "tags" not in element:
                element["tags"] = {}
            nodes_value = []
            for node in element["nodes"]:
                nodes_value.append(nodes_by_id[node])
            element["nodes"] = nodes_value
            elements["ways"].append(element)
        if element["type"] == "relation":
            if "tags" not in element:
                element["tags"] = {}
            elements["relations"].append(element)
