import ror_tobj_file
import config
import ror_waypoint_file
import helper
import math
import osm

road_data = []


def process(entity, osm_data=None):
    if osm_data is None:
        process_way(entity)
    else:
        process_relation(entity, osm_data)


def process_relation(relation, osm_data):
    global road_data
    road_data = []

    road_generated = False

    all_way_nodes = []
    all_way_tags = {}

    for member in relation.members:
        way = osm.get_way_by_id(osm_data, member.ref)
        if way is not None:
            all_way_nodes = all_way_nodes + way.nodes
            all_way_tags.update(way.tags)

    if ("highway" in all_way_tags and all_way_tags["highway"] == "raceway") or (
            "disused:highway" in all_way_tags and all_way_tags["disused:highway"] == "raceway"): # For Melbourne F1 circuit
        if "name" in relation.tags:
            all_way_tags.update({"name": relation.tags["name"]})
            relation.tags.pop("name")
        if "name:en" in relation.tags:
            all_way_tags.update({"name:en": relation.tags["name:en"]})
            relation.tags.pop("name:en")

        road_generated |= generate_road(all_way_nodes, all_way_tags)

        if road_generated:
            ror_waypoint_file.add_waypoint(all_way_nodes, all_way_tags)

            for member in relation.members:
                way = osm.get_way_by_id(osm_data, member.ref)
                if way is not None:
                    way.tags["mapgen"] = "used_by_relation"

    ror_tobj_file.write_road(road_data)


def process_way(way):
    global road_data
    road_data = []

    if generate_road_from_way(way) is True:
        ror_waypoint_file.add_waypoint_from_way(way)
    ror_tobj_file.write_road(road_data)


# Return True if waypoints generation is needed
def generate_road_from_way(way):
    return generate_road(way.nodes, way.tags)


def generate_road(nodes, tags):
    if "level" in tags:
        if tags["level"][0] == '-':  # Skip negative levels
            return False

    # index 0 is the oldest point, index 1 the newest
    x_history = []
    y_history = []
    x = 0.0
    y = 0.0

    road_width = config.data["lane_width"]
    road_height = config.data["road_height"]
    border_width = 0.0
    border_height = 0.0
    road_type = None

    bridge_factor = 0.0

    need_waypoints = False

    found = False

    if "lanes" in tags:
        road_width = int(tags["lanes"]) * config.data["lane_width"]
        tags.pop("lanes")

    if "highway" in tags:
        found = True
        if (tags["highway"] == "footway" or
                tags["highway"] == "pedestrian" or
                tags["highway"] == "path"):
            road_width = 0.0
            road_height = 0.0
            border_width = config.data["footway_width"]
            border_height = config.data["footway_height"]
            if "surface" in tags:
                if tags["surface"] == "asphalt":
                    road_width = config.data["footway_width"]
                    road_height = config.data["road_height"]
                    border_width = 0.0
                    border_height = 0.0
                    tags.pop("surface")

        if tags["highway"] == "raceway":
            need_waypoints = True
            if "sport" in tags:
                if tags["sport"] == "karting":
                    road_width = config.data["raceway_karting_width"]
                    tags.pop("sport")
                else:
                    road_width = config.data["raceway_width"]
                if "surface" in tags:
                    if tags["surface"] == "asphalt":
                        tags.pop("surface")

        if "bridge" in tags and tags["bridge"] == "yes":
            bridge_factor = 1.0
            road_type = "bridge"
            tags.pop("bridge")
        if "layer" in tags:
            try:
                bridge_factor = float(tags["layer"]) - 1.0
                tags.pop("layer")
            except ValueError:
                print("Cannot convert layer: " + tags["layer"])

        if "surface" in tags:
            if tags["surface"] == "asphalt":
                tags.pop("surface")

        tags.pop("highway")

    if "disused:highway" in tags and tags["disused:highway"] == "raceway":
        need_waypoints = True
        road_width = config.data["raceway_width"]
        tags.pop("disused:highway")

    if "sidewalk" in tags:
        if tags["sidewalk"] == "both":
            road_type = "both"
            border_width = config.data["sidewalk_width"]
            border_height = config.data["sidewalk_height"]
        elif tags["sidewalk"] == "left":
            road_type = "left"
            border_width = config.data["sidewalk_width"]
            border_height = config.data["sidewalk_height"]
        elif tags["sidewalk"] == "right":
            road_type = "right"
            border_width = config.data["sidewalk_width"]
            border_height = config.data["sidewalk_height"]

        tags.pop("sidewalk")

    # aeroways
    if "aeroway" in tags:
        if tags["aeroway"] == "runway":
            road_height = config.data["runway_height"]
            road_width = 60.0
            found = True
            tags.pop("aeroway")
        elif tags["aeroway"] == "taxiway":
            road_height = config.data["taxiway_height"]
            road_width = 15.0
            found = True
            tags.pop("aeroway")
        if "width" in tags:
            road_width = tags["width"]
            tags.pop("width")

    # Monorail
    if "railway" in tags:
        if tags["railway"] == "monorail":
            if "bridge" in tags:
                if tags["bridge"] == "viaduct":
                    road_height = config.data["monorail_height"]
                    road_width = 0.90
                    border_width = 0.0
                    border_height = 0.0

                    road_type = "monorail"
                    found = True
                    tags.pop("bridge")
                    tags.pop("railway")

    if found is False:
        return False

    if road_type is None:
        if border_width == 0.0 or border_height == 0.0:
            road_type = "flat"
        else:
            road_type = "both"

    for node in nodes:
        x = helper.lon_to_x(node.lon)
        y = helper.lat_to_y(node.lat)
        z = config.data["ground_line"] + road_height

        if len(x_history) == 0:
            x_history.append(x)
            y_history.append(y)
            continue
        elif len(x_history) == 1:
            # Angle for first road: direction of first two points
            angle = math.degrees(math.atan2(y_history[0] - y, x - x_history[0]))
            add_road(road_data, x_history[0], y_history[0], z, 0.0, 0.0, angle, road_width,
                     border_width,
                     border_height, road_type)
            x_history.append(x)
            y_history.append(y)
            continue
        else:
            # Angle for other road: direction between previous and next point
            angle = math.degrees(math.atan2(y_history[0] - y, x - x_history[0]))
            z += bridge_factor * config.data["bridge_height"]
            add_road(road_data, x_history[1], y_history[1], z, 0.0, 0.0, angle, road_width,
                     border_width,
                     border_height, road_type)
            add_traffic_signals(node, x_history[1], y_history[1], angle, road_width)

            x_history[0] = x_history[1]
            y_history[0] = y_history[1]
            x_history[1] = x
            y_history[1] = y

    # Last road, angle between previous point and last point
    angle = math.degrees(math.atan2(y_history[0] - y, x - x_history[0]))
    z = config.data["ground_line"] + road_height
    add_road(road_data, x_history[1], y_history[1], z, 0.0, 0.0, angle, road_width,
             border_width,
             border_height,
             road_type)

    return need_waypoints


def add_road(all_road_data, x, y, z, rx, ry, rz, road_width, border_width, border_height, road_type):
    # In tobj file rz is just after rx
    all_road_data.append(str(x) + ", " + str(z) + ", " + str(y) + ", " + str(rx) + ", " + str(rz) + ", " + str(
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
