import json
import config
import helper
import gvar
import ror_zip_file

all_ways = []


def add_waypoint(way):
    # with open(gvar.EXPORT_PATH + "/savegames/waypoints.json", "r") as json_file:
    #    data = json.load(json_file)

    all_ways.append(way)


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

        print(str(len(all_ways)) + " circuit branches")

        index = 0
        for way in all_ways:
            if "name" in way.tags:
                name = way.tags["name"]
                way.tags.pop("name")
            elif "name:en" in way.tags:
                name = way.tags["name:en"]
                way.tags.pop("name:en")
            else:
                name = "waypoints_" + str(index)
                index += 1

            waypoint = {
                "terrain": config.data["map_name"] + ".terrn2",
                "preset": name,
                "waypoints":
                    [
                    ]
            }

            for node in way.nodes:
                x = helper.lon_to_x(node.lon)
                y = helper.lat_to_y(node.lat)
                waypoint["waypoints"].append([x, config.data["ground_line"], y])

            data.append(waypoint)

        with open(gvar.EXPORT_PATH + "/savegames/waypoints.json", "w", encoding='utf8') as json_file:
            json.dump(data, json_file, ensure_ascii=False)
