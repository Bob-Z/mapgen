import ror_tobj_file
import config
import ror_waypoint_file
import helper
import math


def process(way):
    if "level" in way.tags:
        if way.tags["level"][0] == '-':  # Skip negative levels
            return

    road_data = []

    # index 0 is the oldest point, index 1 the newest
    x_history = []
    y_history = []
    x = 0.0
    y = 0.0

    road_width = config.data["lane_width"]
    road_height = config.data["road_height"]
    border_width = 0.0
    border_height = 0.0
    road_type = "both"

    bridge_factor = 0.0

    found = False

    if "highway" in way.tags:
        found = True
        if (way.tags["highway"] == "footway" or
                way.tags["highway"] == "pedestrian" or
                way.tags["highway"] == "path"):
            road_width = 0.0
            road_height = 0.0
            border_width = config.data["footway_width"]
            border_height = config.data["footway_height"]
            if "surface" in way.tags:
                if way.tags["surface"] == "asphalt":
                    road_width = config.data["footway_width"]
                    road_height = config.data["road_height"]
                    border_width = 0.0
                    border_height = 0.0
                    way.tags.pop("surface")

        if way.tags["highway"] == "raceway":
            if "sport" in way.tags:
                if way.tags["sport"] == "karting":
                    road_width = config.data["raceway_karting_width"]
                else:
                    road_width = config.data["raceway_width"]
                if "surface" in way.tags:
                    if way.tags["surface"] == "asphalt":
                        way.tags.pop("surface")
            ror_waypoint_file.add_waypoint(way)

        if "bridge" in way.tags and way.tags["bridge"] == "yes":
            bridge_factor = 1.0
            road_type = "bridge"
            way.tags.pop("bridge")
        if "layer" in way.tags:
            bridge_factor = float(way.tags["layer"])
            way.tags.pop("layer")

        way.tags.pop("highway")

    if "sidewalk" in way.tags:
        if way.tags["sidewalk"] == "both":
            road_type = "both"
            border_width = config.data["sidewalk_width"]
            border_height = config.data["sidewalk_height"]
        elif way.tags["sidewalk"] == "left":
            road_type = "left"
            border_width = config.data["sidewalk_width"]
            border_height = config.data["sidewalk_height"]
        elif way.tags["sidewalk"] == "right":
            road_type = "right"
            border_width = config.data["sidewalk_width"]
            border_height = config.data["sidewalk_height"]

        way.tags.pop("sidewalk")

    if "lanes" in way.tags:
        road_width = int(way.tags["lanes"]) * config.data["lane_width"]
        way.tags.pop("lanes")

    # aeroways
    if "aeroway" in way.tags:
        if way.tags["aeroway"] == "runway":
            road_height = config.data["runway_height"]
            road_width = 60.0
            found = True
            way.tags.pop("aeroway")
        elif way.tags["aeroway"] == "taxiway":
            road_height = config.data["taxiway_height"]
            road_width = 15.0
            found = True
            way.tags.pop("aeroway")
        if "width" in way.tags:
            road_width = way.tags["width"]
            way.tags.pop("width")

    # Monorail
    if "railway" in way.tags:
        if way.tags["railway"] == "monorail":
            if "bridge" in way.tags:
                if way.tags["bridge"] == "viaduct":
                    road_height = config.data["monorail_height"]
                    road_width = 0.90
                    border_width = 0.0
                    border_height = 0.0

                    road_type = "monorail"
                    found = True
                    way.tags.pop("bridge")
                    way.tags.pop("railway")

    if found is False:
        return

    for node in way.nodes:
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
    add_road(road_data, x_history[1], y_history[1], config.data["ground_line"], 0.0, 0.0, angle, road_width,
             border_width,
             border_height,
             road_type)

    ror_tobj_file.write_road(road_data)


def add_road(road_data, x, y, z, rx, ry, rz, road_width, border_width, border_height, road_type):
    # In tobj file rz is just after rx
    road_data.append(str(x) + ", " + str(z) + ", " + str(y) + ", " + str(rx) + ", " + str(rz) + ", " + str(
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
