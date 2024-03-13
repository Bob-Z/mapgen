import gvar
import config


def create_file():
    with open(config.data["work_path"] + config.data["map_name"] + ".terrn2", "w") as terrn2_file:
        terrn2_file.write("\
[General]\n\
Name = " + config.data["map_name"] + " generated terrain\n\
GeometryConfig = " + config.data["map_name"] + ".otc" + "\n\
CaelumConfigFile = " + config.data["map_name"] + ".os" + "\n\
Water = 1\n \
WaterLine = " + str(config.data["water_line"]) + "\n\
AmbientColor = 1, 1, 1\n\
StartPosition = " + str(gvar.map_size / 2) + " " + str(config.data["ground_line"]) + " " + str(gvar.map_size / 2) + "\n\
SandStormCubeMap = tracks/skyboxcol\n\
Gravity = -9.81\n\
CategoryID = 129\n\
Version = 1\n\
GUID = 0\n\
[Authors]\n\
terrain = mapgen\n\
[Objects]\n" +
                          config.data["map_name"] + ".tobj=\n" +
                          config.data["map_name"] + "_vegetation.tobj=\n")


def add_waypoints():
    with open(config.data["work_path"] + config.data["map_name"] + ".terrn2", "a") as terrn2_file:
        terrn2_file.write("\
[AI Presets]\n\
waypoints.json=\n")
