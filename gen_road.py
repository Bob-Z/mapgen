import ror_tobj_file
import config
import ror_waypoint_file
import helper
import math
import osm

all_road_data = []
index = 1


def process(entity, osm_data=None):
    if osm_data is None:
        process_way(entity)
    else:
        process_relation(entity, osm_data)


def process_relation(relation, osm_data):
    for member in relation.members:
        way = osm.get_way_by_id(osm_data, member.ref)
        if way is not None:
            if "type" in relation.tags and relation.tags["type"] == "circuit":
                if member.role != "pit_lane" and member.role != "pitlane":
                    if "name:en" in relation.tags:
                        circuit_name = relation.tags["name:en"]
                    elif "name" in relation.tags:
                        circuit_name = relation.tags["name"]
                    else:
                        global index
                        circuit_name = "circuit " + str(index)
                        index += 1

                    old_tag = way.tags
                    way.tags["name"] = circuit_name
                    way.tags["name:en"] = circuit_name
                    way.tags["highway"] = "raceway"

                    if append_road(way, link_road=True) is True:
                        way.tags["mapgen"] = "used_by_relation"
                        relation.tags["mapgen"] = "used_by_relation"

                    way.tags = old_tag


def process_way(way):
    if "mapgen" in way.tags and way.tags["mapgen"] == "used_by_relation":
        return
    append_road(way)


# Return True if a road has been appended
def append_road(way, link_road=False):
    road_config = generate_road_config(way.tags)
    if road_config is None:
        return False
    else:
        name = ""
        if "name:en" in way.tags:
            name = way.tags["name:en"]
        elif "name" in way.tags:
            name = way.tags["name"]

        if (link_road is True or road_config["need_waypoints"] is True) and name != "":
            # append roads with the same name
            already_exist = False
            for my_road_data in all_road_data:
                if my_road_data["name"] == name:
                    my_road_data["nodes"].append(way.nodes)
                    already_exist = True
                    break
            if already_exist is False:
                all_road_data.append({"name": name, "road_config": road_config, "tags": way.tags, "nodes": [way.nodes]})
        else:
            all_road_data.append({"name": name, "road_config": road_config, "tags": way.tags, "nodes": [way.nodes]})

        return True


def generate_road_config(tags):
    if "level" in tags:
        if tags["level"][0] == '-':  # Skip negative levels
            return None

    if "area" in tags and tags["area"] == "yes":
        return None

    if "network" in tags:
        return None

    road_config = {
        "road_width": config.data["lane_width"],
        "road_height": config.data["road_height"],
        "border_width": 0.0,
        "border_height": 0.0,
        "road_type": None,
        "need_waypoints": False,
        "bridge_factor": 0.0,
    }

    found = False

    if "lanes" in tags:
        road_config["road_width"] = int(tags["lanes"]) * config.data["lane_width"]
        tags.pop("lanes")

    if "highway" in tags:
        if (tags["highway"] == "footway" or
                tags["highway"] == "pedestrian" or
                tags["highway"] == "path"):
            road_config["road_width"] = 0.0
            road_config["road_height"] = 0.0
            road_config["border_width"] = config.data["footway_width"]
            road_config["border_height"] = config.data["footway_height"]
            if "surface" in tags:
                if tags["surface"] == "asphalt":
                    road_config["road_width"] = config.data["footway_width"]
                    road_config["road_height"] = config.data["road_height"]
                    road_config["border_width"] = 0.0
                    road_config["border_height"] = 0.0
                    tags.pop("surface")

        if tags["highway"] == "raceway":
            road_config["need_waypoints"] = True
            road_config["road_width"] = config.data["raceway_width"]
            if "sport" in tags:
                if tags["sport"] == "karting":
                    road_config["road_width"] = config.data["raceway_karting_width"]
                    tags.pop("sport")
            if "surface" in tags:
                if tags["surface"] == "asphalt":
                    tags.pop("surface")

        if "bridge" in tags and tags["bridge"] == "yes":
            road_config["bridge_factor"] = 1.0
            road_config["road_type"] = "bridge"
            tags.pop("bridge")
        if "layer" in tags:
            try:
                road_config["bridge_factor"] = float(tags["layer"]) - 1.0
                tags.pop("layer")
            except ValueError:
                print("Cannot convert layer: " + tags["layer"])

        if "surface" in tags:
            if tags["surface"] == "asphalt":
                tags.pop("surface")

        tags.pop("highway")

        found = True

    if "disused:highway" in tags and tags["disused:highway"] == "raceway":
        road_config["need_waypoints"] = True
        road_config["road_width"] = config.data["raceway_width"]

        tags.pop("disused:highway")

        found = True

    # if "sidewalk" in tags:
    #    if tags["sidewalk"] == "both":
    #        road_config["road_type"] = "both"
    #        road_config["border_width"] = config.data["sidewalk_width"]
    #        road_config["border_height"] = config.data["sidewalk_height"]
    #    elif tags["sidewalk"] == "left":
    #        road_config["road_type"] = "left"
    #        road_config["border_width"] = config.data["sidewalk_width"]
    #        road_config["border_height"] = config.data["sidewalk_height"]
    #    elif tags["sidewalk"] == "right":
    #        road_config["road_type"] = "right"
    #        road_config["border_width"] = config.data["sidewalk_width"]
    #        road_config["border_height"] = config.data["sidewalk_height"]

    #    tags.pop("sidewalk")

    # aeroways
    if "aeroway" in tags:
        if tags["aeroway"] == "runway":
            road_config["road_height"] = config.data["runway_height"]
            road_config["road_width "] = 60.0

            tags.pop("aeroway")

            found = True
        elif tags["aeroway"] == "taxiway":
            road_config["road_height"] = config.data["taxiway_height"]
            road_config["road_width"] = 15.0

            tags.pop("aeroway")

            found = True

        if "width" in tags:
            road_config["road_width"] = tags["width"]
            tags.pop("width")

    # Monorail
    if "railway" in tags:
        if tags["railway"] == "monorail":
            if "bridge" in tags:
                if tags["bridge"] == "viaduct":
                    road_config["road_height"] = config.data["monorail_height"]
                    road_config["road_width"] = 0.90
                    road_config["border_width"] = 0.0
                    road_config["border_height"] = 0.0

                    road_config["road_type"] = "monorail"

                    tags.pop("bridge")
                    tags.pop("railway")

                    found = True

    if found is False:
        return None

    if road_config["road_type"] is None:
        if road_config["border_width"] == 0.0 or road_config["border_height"] == 0.0:
            road_config["road_type"] = "flat"
        else:
            road_config["road_type"] = "both"

    return road_config


def generate_road_from_config(road_config, nodes):
    road_data = []

    x_history = []
    y_history = []
    x = 0.0
    y = 0.0

    for node in nodes:
        x = helper.lon_to_x(node.lon)
        y = helper.lat_to_y(node.lat)
        z = config.data["ground_line"] + road_config["road_height"]

        if len(x_history) == 0:
            x_history.append(x)
            y_history.append(y)
            continue
        elif len(x_history) == 1:
            # Angle for first road: direction of first two points
            angle = math.degrees(math.atan2(y_history[0] - y, x - x_history[0]))
            add_road(road_data, x_history[0], y_history[0], z, 0.0, 0.0, angle, road_config["road_width"],
                     road_config["border_width"],
                     road_config["border_height"], road_config["road_type"])
            x_history.append(x)
            y_history.append(y)
            continue
        else:
            # Angle for other road: direction between previous and next point
            angle = math.degrees(math.atan2(y_history[0] - y, x - x_history[0]))
            z += road_config["bridge_factor"] * config.data["bridge_height"]
            add_road(road_data, x_history[1], y_history[1], z, 0.0, 0.0, angle, road_config["road_width"],
                     road_config["border_width"],
                     road_config["border_height"], road_config["road_type"])
            add_traffic_signals(node, x_history[1], y_history[1], angle, road_config["road_width"])

            x_history[0] = x_history[1]
            y_history[0] = y_history[1]
            x_history[1] = x
            y_history[1] = y

    # Last road, angle between previous point and last point
    angle = math.degrees(math.atan2(y_history[0] - y, x - x_history[0]))
    z = config.data["ground_line"] + road_config["road_height"]
    add_road(road_data, x_history[1], y_history[1], z, 0.0, 0.0, angle, road_config["road_width"],
             road_config["border_width"],
             road_config["border_height"],
             road_config["road_type"])

    return road_data


def add_road(my_road_data, x, y, z, rx, ry, rz, road_width, border_width, border_height, road_type):
    # In tobj file rz is just after rx
    my_road_data.append(str(x) + ", " + str(z) + ", " + str(y) + ", " + str(rx) + ", " + str(rz) + ", " + str(
        ry) + ", " + str(road_width) + ", " + str(border_width) + ", " + str(border_height) + ", " + road_type + "\n")


def add_traffic_signals(node, road_x, road_y, angle, road_width):
    if "highway" in node.tags:
        if node.tags["highway"] == "traffic_signals":
            node.tags.pop("highway")
            angle -= 90
            if "traffic_signals:direction" in node.tags:
                if node.tags["traffic_signals:direction"] == "backward":
                    angle += 90
                node.tags.pop("traffic_signals:direction")

            signal_x = road_x + (math.cos(math.radians(angle)) * road_width / 2.0)
            signal_y = road_y - (math.sin(math.radians(angle)) * road_width / 2.0)

            ror_tobj_file.add_object(signal_x, signal_y, 0.0, 0.0, 0.0, angle, "trafficlightsequence1")


def write_all_roads():
    for my_road_data in all_road_data:

        # Link roads with the same name
        ready_nodes = osm.concat_way_by_distance(my_road_data["nodes"])

        road_data = generate_road_from_config(my_road_data["road_config"], ready_nodes)

        if my_road_data["road_config"]["need_waypoints"]:
            ror_waypoint_file.add_waypoint(ready_nodes, my_road_data["name"])

        ror_tobj_file.write_road(road_data)
