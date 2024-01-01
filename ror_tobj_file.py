import config
import gvar


def add_object(x, y, z, rx, ry, rz, name):
    new_line = str(x) + ", " + str(z + gvar.GROUND_LEVEL) + ", " + str(y) + ", " + str(rx) + ", " + str(
        rz) + ", " + str(
        ry) + ", " + name + "\n"

    with open(config.data["work_path"] + config.data["map_name"] + ".tobj", "a") as tobj_file:
        tobj_file.write(new_line)


def write_road(road_data):
    if len(road_data) > 0:
        with open(config.data["work_path"] + config.data["map_name"] + ".tobj", "a") as tobj_file:
            tobj_file.write("begin_procedural_roads\n")
            for road in road_data:
                tobj_file.write(road)
            tobj_file.write("end_procedural_roads\n")
