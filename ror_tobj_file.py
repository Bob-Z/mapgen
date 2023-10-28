import gvar
import overpy
import helper
import math

road_data = []

ROAD_HEIGHT = 0.01
LANE_WIDTH = 3.0
FOOTWAY_WIDTH = 1.5
FOOTWAY_HEIGHT = 0.02


def create_road(way):
    begin_road()

    # index 0 is the oldest point, index 1 the newest
    x_history = []
    y_history = []
    x = 0.0
    y = 0.0

    road_width = LANE_WIDTH
    road_height = ROAD_HEIGHT
    border_width = 0
    border_height = 0

    if "highway" in way.tags:
        if way.tags["highway"] == "footway":
            road_width = 0
            road_height = 0
            border_width = FOOTWAY_WIDTH
            border_height = FOOTWAY_HEIGHT
            if "surface" in way.tags:
                if way.tags["surface"] == "asphalt":
                    road_width = FOOTWAY_WIDTH
                    road_height = ROAD_HEIGHT
                    border_width = 0
                    border_height = 0
                    way.tags.pop("surface")

        way.tags.pop("highway")

    if "surface" in way.tags:
        # Asphalt is the default surface
        # TODO manage other type of surface
        if way.tags["surface"] == "asphalt":
            way.tags.pop("surface")

    if "lanes" in way.tags:
        road_width = int(way.tags["lanes"]) * LANE_WIDTH
        way.tags.pop("lanes")

    try:
        # all_nodes = way.get_nodes(resolve_missing=True)
        # for node in all_nodes:
        for node in way.nodes:
            x = helper.lat_to_x(node.lat)
            y = helper.lon_to_y(node.lon)

            if len(x_history) == 0:
                x_history.append(x)
                y_history.append(y)
                continue
            elif len(x_history) == 1:
                # Angle for first road: direction of first two points
                angle = math.degrees(math.atan2(y_history[0] - y, x - x_history[0]))
                add_road(x_history[0], y_history[0], road_height, 0.0, 0.0, angle, road_width, border_width,
                         border_height)
                x_history.append(x)
                y_history.append(y)
                continue
            else:
                # Angle for other road: direction between previous and next point
                angle = math.degrees(math.atan2(y_history[0] - y, x - x_history[0]))
                add_road(x_history[1], y_history[1], road_height, 0.0, 0.0, angle, road_width, border_width,
                         border_height)
                add_traffic_signals(node, x_history[1], y_history[1], road_height, angle, road_width)

                x_history[0] = x_history[1]
                y_history[0] = y_history[1]
                x_history[1] = x
                y_history[1] = y

        # Last road, angle between previous point and last point
        angle = math.degrees(math.atan2(y_history[0] - y, x - x_history[0]))
        add_road(x_history[1], y_history[1], road_height, 0.0, 0.0, angle, road_width, border_width, border_height)

    except overpy.exception.DataIncomplete:
        # print("Missing nodes: ", way, way.tags)
        pass

    end_road()


def add_object(obj):
    with open(gvar.WORK_PATH + gvar.MAP_NAME + ".tobj", "a") as tobj_file:
        if "icon" in obj:
            new_line = str(obj["x"]) + ", " + str(obj["z"]) + ", " + str(obj["y"]) + ", " + str(obj["rx"]) + ", " + str(
                obj["rz"]) + ", " + str(
                obj["ry"]) + ", " + obj["name"] + " " + obj["icon"] + "\n"
        else:
            new_line = str(obj["x"]) + ", " + str(obj["z"]) + ", " + str(obj["y"]) + ", " + str(obj["rx"]) + ", " + str(
                obj["rz"]) + ", " + str(
                obj["ry"]) + ", " + obj["name"] + "\n"
        tobj_file.write(new_line)


def begin_road():
    global road_data
    road_data = []


def add_road(x, y, z, rx, ry, rz, road_width, border_width, border_height):
    global road_data
    # In tobj file rz is just after rx
    road_data.append(str(x) + ", " + str(z) + ", " + str(y) + ", " + str(rx) + ", " + str(rz) + ", " + str(
        ry) + ", " + str(road_width) + ", " + str(border_width) + ", " + str(border_height) + ", both\n")


def add_traffic_signals(node, road_x, road_y, road_height, angle, road_width):
    if "highway" in node.tags:
        if node.tags["highway"] == "traffic_signals":

            angle -= 90  # Don't know why this is needed, byt it seems to work
            if "traffic_signals:direction" in node.tags:
                if node.tags["traffic_signals:direction"] == "backward":
                    angle += 90

            signal_x = road_x + (math.cos(math.radians(angle)) * road_width / 2.0)
            signal_y = road_y - (math.sin(math.radians(angle)) * road_width / 2.0)

            new_signal = {"x": signal_x, "y": signal_y, "z": road_height, "rx": 0.0, "ry": 0.0, "rz": angle,
                          "name": "trafficlightsequence1"}
            add_object(new_signal)


def end_road():
    global road_data

    if len(road_data) > 0:
        with open(gvar.WORK_PATH + gvar.MAP_NAME + ".tobj", "a") as tobj_file:
            tobj_file.write("begin_procedural_roads\n")
            for road in road_data:
                tobj_file.write(road)
            tobj_file.write("end_procedural_roads\n")
