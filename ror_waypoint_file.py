import json
import config
import helper
import ror_zip_file
import ror_terrn2_file

all_roads = []


def add_waypoint(nodes, name):
    all_roads.append([nodes, name])


def write():
    if len(all_roads) > 0:
        data = [
            {
                "terrains":
                    [
                        config.data["map_name"]
                    ]
            }
        ]

        print(str(len(all_roads)) + " waypoints circuits")

        index = 0
        for road in all_roads:
            name = road[1]
            if name is None or name == "":
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

            for node in road[0]:
                x = helper.lon_to_x(node.lon)
                y = helper.lat_to_y(node.lat)
                waypoint["waypoints"].append([x, config.data["ground_line"], y])

            data.append(waypoint)

        with open(config.data["work_path"] + "waypoints.json", "w") as json_file:
            json.dump(data, json_file, ensure_ascii=False)

        ror_terrn2_file.add_waypoints()
        ror_zip_file.add_to_zip_file_list("waypoints.json")
