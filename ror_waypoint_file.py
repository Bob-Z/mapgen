import json
import config
import helper
import gvar
import ror_zip_file

all_ways = []


def add_waypoint_from_way(way):
    all_ways.append([way.nodes, way.tags])


def add_waypoint(nodes, tags):
    all_ways.append([nodes, tags])


def write():
    if len(all_ways) > 0:
        data = [
            {
                "terrains":
                    [
                        config.data["map_name"]
                    ]
            }
        ]

        print(str(len(all_ways)) + " circuits")

        index = 0
        for way in all_ways:
            if "name:en" in way[1]:
                name = way[1]["name:en"]
                way[1].pop("name:en")
            elif "name" in way[1]:
                name = way[1]["name"]
                way[1].pop("name")
            else:
                name = ("waypoints")
            name = name + " (" + str(index) + ")"
            index += 1

            waypoint = {
                "terrain": config.data["map_name"] + ".terrn2",
                "preset": name,
                "waypoints":
                    [
                    ]
            }

            for node in way[0]:
                x = helper.lon_to_x(node.lon)
                y = helper.lat_to_y(node.lat)
                waypoint["waypoints"].append([x, config.data["ground_line"], y])

            data.append(waypoint)

        with open(gvar.EXPORT_PATH + "/savegames/waypoints.json", "w", encoding='utf8') as json_file:
            json.dump(data, json_file, ensure_ascii=False)
