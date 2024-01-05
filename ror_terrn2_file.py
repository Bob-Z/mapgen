import gvar
import config


def create_file(map_width, map_length):
    with open(config.data["work_path"] + config.data["map_name"] + ".terrn2", "w") as terrn2_file:
        terrn2_file.write("[General]\n\
    Name = mapgen terrain\n\
    GeometryConfig = " + config.data["map_name"] + ".otc" + "\n\
    CaelumConfigFile = " + config.data["map_name"] + ".os" + "\n")

    if gvar.is_water_map is False:
        with open(config.data["work_path"] + config.data["map_name"] + ".terrn2", "a") as terrn2_file:
            terrn2_file.write("            Water = 0\n")
    else:
        with open(config.data["work_path"] + config.data["map_name"] + ".terrn2", "a") as terrn2_file:
            terrn2_file.write("            Water = 1\n\
    WaterLine = " + str(config.data["water_line"]) + "\n")

    with open(config.data["work_path"] + config.data["map_name"] + ".terrn2", "a") as terrn2_file:
        terrn2_file.write("    AmbientColor = 1, 1, 1\n\
    StartPosition = " + str(map_length / 2) + " " + str(gvar.GROUND_LEVEL) + " " + str(map_width / 2) + "\n\
    SandStormCubeMap = tracks/skyboxcol\n\
    Gravity = -9.81\n\
    CategoryID = 129\n\
    Version = 1\n\
    GUID = 0\n\
    [Authors]\n\
    terrain = mapgen\n\
    [Objects]\n" + config.data["map_name"] + ".tobj=\n")
