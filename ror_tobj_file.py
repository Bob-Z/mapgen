import config
import gvar
import ogre_map_vegetation


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


def add_tree(osm_data, entity, scaleFrom, scaleTo, density, mesh_name, collision_mesh_name):
    map_file_name = ogre_map_vegetation.add_tree_map(osm_data, entity, 0xff)
    # trees yawFrom, yawTo, scaleFrom, scaleTo, highDensity, distance1, distance2, meshName colormap densitymap gridspacing collmesh
    new_line = "trees 0, 360, " + str(scaleFrom) + ", " + str(scaleTo) + ", 1.0, 250, " + str(
        gvar.map_size) + "," + mesh_name + " none " + map_file_name + " " + str(
        density) + "  " + collision_mesh_name + "\n"

    with open(config.data["work_path"] + config.data["map_name"] + "_vegetation.tobj", "a") as tobj_file:
        tobj_file.write(new_line)
