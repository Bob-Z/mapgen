import math

import helper
import gvar
import overpy
import os
import ror_zip_file
import triangulate
from gvar import WORK_PATH

# Arbitrary constants
BUILDING_LEVEL_HEIGHT = 2.5
GRASS_HEIGHT = 0.006
SWIMMING_POOL_HEIGHT = 0.07
AMENITY_HEIGHT = 0.006
DEFAULT_TEXTURE = "mapgen_beige"
DEFAULT_BARRIER_WIDTH = 0.3
DEFAULT_BARRIER_HEIGHT = 1.5
DEFAULT_WATER_HEIGHT = 0.005

VERTEX_PER_WALL = 4

building_name = ""
building_index = 0

# Modified by tags
build_barrier = False
collision = True
wall_height = BUILDING_LEVEL_HEIGHT
texture_name = DEFAULT_TEXTURE
barrier_width = DEFAULT_BARRIER_WIDTH


def create_mesh(way):
    global building_name
    global building_index

    building_index = building_index + 1

    building_name = "building" + str(building_index)

    if process_tags(way) is False:
        return None

    new_object, vertex, vertex2d = get_vertex(way)
    if new_object is None:
        return None

    vertex_index, face_qty, wall_vertex_str, wall_face_str = generate_wall(vertex)
    if wall_vertex_str is None:
        return None
    vertex_index, face_qty, root_vertex_str, roof_face_str = generate_roof(vertex2d, vertex_index, face_qty)

    generate_mesh_file(vertex_index, face_qty, wall_vertex_str + root_vertex_str, wall_face_str + roof_face_str)

    if "name" in way.tags:
        # FIXME "station" is a default choice, may be improved ?
        new_object["icon"] = "station " + way.tags["name"]
        way.tags.pop("name")

    new_object["z"] = 0.0
    new_object["rx"] = 0.0
    new_object["ry"] = 0.0
    new_object["rz"] = 0.0
    new_object["name"] = building_name
    new_object["collision"] = collision

    return new_object


def process_tags(way):
    global build_barrier
    global collision
    global wall_height
    global texture_name
    global barrier_width

    build_barrier = False
    collision = True
    wall_height = BUILDING_LEVEL_HEIGHT
    texture_name = DEFAULT_TEXTURE
    barrier_width = DEFAULT_BARRIER_WIDTH

    process_ok = True

    levels = 1
    if "building:levels" in way.tags:
        levels = way.tags["building:levels"]
        way.tags.pop("building:levels")

    wall_height = float(levels) * BUILDING_LEVEL_HEIGHT

    if "amenity" in way.tags:
        if way.tags["amenity"] == "shelter":
            texture_name = "mapgen_red"
            way.tags.pop("amenity")
        elif way.tags["amenity"] == "hospital":
            texture_name = "mapgen_grey"
            wall_height = AMENITY_HEIGHT
            way.tags.pop("amenity")
        elif way.tags["amenity"] == "fountain":
            texture_name = "mapgen_blue"
            wall_height = DEFAULT_WATER_HEIGHT
            way.tags.pop("amenity")
        else:
            process_ok = False

    if "landuse" in way.tags:
        if way.tags["landuse"] == "grass":
            texture_name = "mapgen_grass"
            wall_height = GRASS_HEIGHT
            collision = False
            way.tags.pop("landuse")
        elif way.tags["landuse"] == "retail":
            texture_name = "mapgen_grey"
            wall_height = AMENITY_HEIGHT
            way.tags.pop("landuse")
        else:
            process_ok = False

    if "leisure" in way.tags:
        if way.tags["leisure"] == "park":
            texture_name = "mapgen_grass_dandelion"
            wall_height = GRASS_HEIGHT
            collision = False
            way.tags.pop("leisure")
        elif way.tags["leisure"] == "swimming_pool":
            texture_name = "mapgen_swimming_pool"
            wall_height = SWIMMING_POOL_HEIGHT
            collision = False
            way.tags.pop("leisure")
        else:
            process_ok = False

    if "barrier" in way.tags:
        if way.tags["barrier"] == "wall":
            build_barrier = True
            wall_height = DEFAULT_BARRIER_HEIGHT
            texture_name = "mapgen_green"
            way.tags.pop("barrier")
        else:
            process_ok = False

    if "waterway" in way.tags:
        wall_height = DEFAULT_WATER_HEIGHT
        texture_name = "mapgen_blue"
        way.tags.pop("waterway")

    if "natural" in way.tags:
        if way.tags["natural"] == "water":
            wall_height = DEFAULT_WATER_HEIGHT
            texture_name = "mapgen_blue"
            way.tags.pop("natural")
        else:
            process_ok = False

    return process_ok


def generate_wall(vertex):
    global wall_height

    vertex_str = ""
    face_str = ""
    vertex_index = 0
    face_qty = 0
    vertex_qty = len(vertex)

    try:
        for i in range(vertex_qty):
            # Create 4 vertex for a single wall
            # 1-3
            # | |
            # 0-2

            # Do not create face when nodes are the same
            if ((vertex[i][0] == vertex[(i + 1) % vertex_qty][0]) and
                    (vertex[i][1] == vertex[(i + 1) % vertex_qty][1]) and
                    (vertex[i][2] == vertex[(i + 1) % vertex_qty][2])):
                continue

            v0 = [vertex[i][0], vertex[i][1], vertex[i][2]]
            v1 = [vertex[i][0], vertex[i][1], vertex[i][2] + wall_height]
            v2 = [vertex[(i + 1) % vertex_qty][0], vertex[(i + 1) % vertex_qty][1],
                  vertex[(i + 1) % vertex_qty][2]]
            v3 = [vertex[(i + 1) % vertex_qty][0], vertex[(i + 1) % vertex_qty][1],
                  vertex[(i + 1) % vertex_qty][2] + wall_height]

            vertex_str += create_vertex_str(v0, v2, v1, 0.0, 0.0)
            vertex_str += create_vertex_str(v1, v0, v3, 0.0, 1.0)
            vertex_str += create_vertex_str(v2, v3, v0, 1.0, 0.0)
            vertex_str += create_vertex_str(v3, v1, v2, 1.0, 1.0)

            # Create 2 faces (triangle) per wall
            vertex_index = i * VERTEX_PER_WALL
            face_str += create_face(vertex_index + 1, vertex_index, vertex_index + 2)
            face_str += create_face(vertex_index + 2, vertex_index + 3, vertex_index + 1)

            face_qty += 2

        vertex_index += VERTEX_PER_WALL

    except overpy.exception.DataIncomplete:
        # Node unavailable
        pass

    return vertex_index, face_qty, vertex_str, face_str


def generate_roof(vertex2d, vertex_index, face_qty):
    vertex_str = ""
    face_str = ""

    vertex = vertex2d[::-1] if triangulate.IsClockwise(
        vertex2d) else vertex2d[:]
    while len(vertex) >= 3:
        ear = triangulate.GetEar(vertex)
        if not ear:
            break

        # Add Z axis
        ear[0].append(wall_height)
        ear[1].append(wall_height)
        ear[2].append(wall_height)
        # TODO U,V are wrong here
        vertex_str += create_vertex_with_normal_str(ear[0], [0.0, 0.0, 1.0], 0.0, 0.0)
        vertex_str += create_vertex_with_normal_str(ear[1], [0.0, 0.0, 1.0], 0.0, 1.0)
        vertex_str += create_vertex_with_normal_str(ear[2], [0.0, 0.0, 1.0], 1.0, 0.0)

        face_str += create_face(vertex_index + 1, vertex_index + 2, vertex_index + 0)

        vertex_index += 3
        face_qty += 1

    return vertex_index, face_qty, vertex_str, face_str


def get_vertex(way):
    global build_barrier

    all_vertex = []
    min_x = 9999999.0
    min_y = 9999999.0
    max_x = -9999999.0
    max_y = -9999999.0

    try:
        for node in way.nodes:
            x = helper.lat_to_x(node.lat)
            y = helper.lon_to_y(node.lon)

            if x < min_x:
                min_x = x
            if x > max_x:
                max_x = x

            if y < min_y:
                min_y = y
            if y > max_y:
                max_y = y

            all_vertex.append([x, y, 0.0])

        # Coordinate of object on map
        center_x = (max_x + min_x) / 2
        center_y = (max_y + min_y) / 2

        # Make sure vertices are centered on 0,0
        centered_vertex = []
        centered_vertex2d = []

        for v in all_vertex:
            # Y axis is inverted on RoR map
            centered_vertex.append([v[0] - center_x, -(v[1] - center_y), v[2]])
            centered_vertex2d.append([v[0] - center_x, -(v[1] - center_y)])

        if build_barrier is True:
            # Create vertices "around" each segment
            first_side_vertex = []
            first_side_vertex2d = []
            opposite_side_vertex = []
            opposite_side_vertex2d = []

            normal_x = 0.0
            normal_y = 0.0

            for i in range(len(centered_vertex) - 1):
                normal_x = -(centered_vertex2d[i + 1][1] - centered_vertex2d[i][1])
                normal_y = centered_vertex2d[i + 1][0] - centered_vertex2d[i][0]
                normal_norm = math.sqrt((normal_x * normal_x) + (normal_y * normal_y))
                normal_x = (normal_x / normal_norm) * (barrier_width / 2.0)
                normal_y = (normal_y / normal_norm) * (barrier_width / 2.0)

                first_side_vertex.append(
                    [centered_vertex[i][0] + normal_x, centered_vertex[i][1] + normal_y, centered_vertex[i][2]])
                opposite_side_vertex.append(
                    [centered_vertex[i][0] - normal_x, centered_vertex[i][1] - normal_y, centered_vertex[i][2]])

                first_side_vertex2d.append([centered_vertex2d[i][0] + normal_x, centered_vertex2d[i][1] + normal_y])
                opposite_side_vertex2d.append([centered_vertex2d[i][0] - normal_x, centered_vertex2d[i][1] - normal_y])

            # Use latest normal for last input vertex
            i = len(centered_vertex) - 1
            first_side_vertex.append(
                [centered_vertex[i][0] + normal_x, centered_vertex[i][1] + normal_y, centered_vertex[i][2]])
            opposite_side_vertex.append(
                [centered_vertex[i][0] - normal_x, centered_vertex[i][1] - normal_y, centered_vertex[i][2]])

            first_side_vertex2d.append([centered_vertex2d[i][0] + normal_x, centered_vertex2d[i][1] + normal_y])
            opposite_side_vertex2d.append([centered_vertex2d[i][0] - normal_x, centered_vertex2d[i][1] - normal_y])

            first_side_vertex.reverse()
            first_side_vertex2d.reverse()
            centered_vertex = opposite_side_vertex + first_side_vertex
            centered_vertex2d = opposite_side_vertex2d + first_side_vertex2d

        new_object = {"x": center_x, "y": center_y}

        return new_object, centered_vertex, centered_vertex2d

    except overpy.exception.DataIncomplete:
        # Node unavailable
        return None, None, None


def create_vertex_str(v0, v1, v2, u, v):
    vertex_str = "<vertex>\n"
    vertex_str = vertex_str + "<position x=\"" + str(v0[0]) + "\" y=\"" + str(v0[1]) + "\" z=\"" + str(
        v0[2]) + "\" />\n"
    normal = helper.calc_norm([v0, v1, v2])
    vertex_str = vertex_str + "<normal x=\"" + str(normal[0]) + "\" y=\"" + str(normal[1]) + "\" z=\"" + str(
        normal[2]) + "\" />\n"
    vertex_str = vertex_str + "<texcoord u=\"" + str(u) + "\" v=\"" + str(v) + "\" />"
    return vertex_str + "</vertex>\n"


def create_vertex_with_normal_str(v0, normal, u, v):
    vertex_str = "<vertex>\n"
    vertex_str = vertex_str + "<position x=\"" + str(v0[0]) + "\" y=\"" + str(v0[1]) + "\" z=\"" + str(
        v0[2]) + "\" />\n"
    vertex_str = vertex_str + "<normal x=\"" + str(normal[0]) + "\" y=\"" + str(normal[1]) + "\" z=\"" + str(
        normal[2]) + "\" />\n"
    vertex_str = vertex_str + "<texcoord u=\"" + str(u) + "\" v=\"" + str(v) + "\" />"
    return vertex_str + "</vertex>\n"


def create_face(i0, i1, i2):
    return "<face v1=\"" + str(i0) + "\" v2=\"" + str(
        i1) + "\" v3=\"" + str(
        i2) + "\" />\n"


def generate_mesh_file(vertex_index, face_qty, vertex_str, face_str):
    global texture_name

    mesh_file_name = building_name + ".mesh"
    with open(gvar.WORK_PATH + mesh_file_name + ".xml", "w") as mesh_file:
        mesh_file.write("<mesh>\n<submeshes>\n<submesh material=\"" + texture_name + "\" usesharedvertices=\"false\" use32bitindexes=\"false\" operationtype=\"triangle_list\">\n\
<faces count=\"" + str(face_qty) + "\">\n")
        mesh_file.write(face_str)
        mesh_file.write("</faces>\n")
        mesh_file.write("<geometry vertexcount=\"" + str(vertex_index) + "\">\n\
<vertexbuffer positions=\"true\" normals=\"true\" texture_coord_dimensions_0=\"float2\" texture_coords=\"1\">")
        mesh_file.write(vertex_str)
        mesh_file.write("</vertexbuffer>\n</geometry>\n</submesh>\n</submeshes>\n</mesh>\n")

    os.system(
        "OgreXMLConverter " + WORK_PATH + building_name + ".mesh.xml > /dev/null")

    ror_zip_file.add_file(building_name + ".mesh")
