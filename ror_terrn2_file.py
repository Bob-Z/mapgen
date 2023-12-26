import gvar
import config


def create_file(map_width, map_height):
    with open(config.config["work_path"] + config.config["map_name"] + ".terrn2", "w") as terrn2_file:
        terrn2_file.write("[General]\n\
    Name = mapgen terrain\n\
    GeometryConfig = " + config.config["map_name"] + ".otc" + "\n\
    CaelumConfigFile = " + config.config["map_name"] + ".os" + "\n")

    if gvar.is_water_map is False:
        with open(config.config["work_path"] + config.config["map_name"] + ".terrn2", "a") as terrn2_file:
            terrn2_file.write("            Water = 0\n")
    else:
        with open(config.config["work_path"] + config.config["map_name"] + ".terrn2", "a") as terrn2_file:
            terrn2_file.write("            Water = 1\n\
    WaterLine = " + str(config.config["water_line"]) + "\n")

    with open(config.config["work_path"] + config.config["map_name"] + ".terrn2", "a") as terrn2_file:
        terrn2_file.write("    AmbientColor = 1, 1, 1\n\
    StartPosition = " + str(int(map_width / 2)) + " 0 " + str(int(map_height / 2)) + "\n\
    SandStormCubeMap = tracks/skyboxcol\n\
    Gravity = -9.81\n\
    CategoryID = 129\n\
    Version = 1\n\
    GUID = 0\n\
    [Authors]\n\
    terrain = mapgen\n\
    [Objects]\n" + config.config["map_name"] + ".tobj=\n")
