import math
import helper
import os
import ror_zip_file
import triangulate
import config
import ror_tobj_file
import ror_odef_file

VERTEX_PER_WALL = 4

object_index = 0


def create_all_object_file(nodes, height=config.data["building_level_height"], z=0.0,
                           wall_texture=config.data["wall_texture"], roof_texture=config.data["roof_texture"],
                           is_barrier=False, roof_texture_generator=None):
    global object_index

    if height is None:
        height = config.data["building_level_height"]
    if z is None:
        z = 0.0

    object_index = object_index + 1

    obj_name = "obj" + str(object_index)

    if hasattr(nodes[0], 'lat'):
        center_x, center_y, width, length, vertex = get_info_from_input_data(nodes, is_node=True)
    else:
        center_x, center_y, width, length, vertex = get_info_from_input_data(nodes, is_node=False)

    if is_barrier is True:
        vertex = create_additional_vertex_for_barrier(vertex)

    wall_vertex_index, wall_face_qty, wall_vertex_str, wall_face_str = generate_wall(vertex, height)
    if wall_vertex_str is None:
        return None

    if roof_texture_generator is not None:
        roof_texture = roof_texture_generator(width, length)

    # no submeshes with the same texture is allowed
    if wall_texture == roof_texture:
        roof_vertex_index, roof_face_qty, roof_vertex_str, roof_face_str = generate_roof(vertex, height,
                                                                                         wall_vertex_index,
                                                                                         is_barrier)
        generate_mesh_file(
            [{"vertex_index": roof_vertex_index, "face_qty": wall_face_qty + roof_face_qty,
              "vertex_str": wall_vertex_str + roof_vertex_str,
              "face_str": wall_face_str + roof_face_str, "texture": wall_texture}], obj_name)
    else:
        roof_vertex_index, roof_face_qty, roof_vertex_str, roof_face_str = generate_roof(vertex, height, 0, is_barrier)
        generate_mesh_file(
            [{"vertex_index": wall_vertex_index, "face_qty": wall_face_qty, "vertex_str": wall_vertex_str,
              "face_str": wall_face_str, "texture": wall_texture},
             {"vertex_index": roof_vertex_index, "face_qty": roof_face_qty, "vertex_str": roof_vertex_str,
              "face_str": roof_face_str, "texture": roof_texture}], obj_name)

    ror_tobj_file.add_object(center_x, center_y, z, 0.0, 0.0, 0.0, obj_name)
    ror_odef_file.create_file(obj_name, collision=True)


def generate_wall(vertex, height):
    vertex_str = ""
    face_str = ""
    vertex_index = 0
    face_qty = 0
    vertex_qty = len(vertex)

    for i in range(vertex_qty):
        # Create 4 vertex for a single wall
        # 1-3
        # | |
        # 0-2

        v0 = [vertex[i][0], vertex[i][1], 0.0]
        v1 = [vertex[i][0], vertex[i][1], height]
        v2 = [vertex[(i + 1) % vertex_qty][0], vertex[(i + 1) % vertex_qty][1],
              0.0]
        v3 = [vertex[(i + 1) % vertex_qty][0], vertex[(i + 1) % vertex_qty][1],
              height]

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

    return vertex_index, face_qty, vertex_str, face_str


def generate_roof(vertex, height, vertex_index, is_barrier):
    if is_barrier is False:
        return generate_roof_for_building(vertex, height, vertex_index)
    else:
        return generate_roof_for_barrier(vertex, height, vertex_index)


def generate_roof_for_building(vertex2d, height, vertex_index):
    face_qty = 0
    vertex_str = ""
    face_str = ""

    vertex = vertex2d[::-1] if triangulate.IsClockwise(
        vertex2d) else vertex2d[:]
    while len(vertex) >= 3:
        ear = triangulate.GetEar(vertex)
        if not ear:
            break

        # Add Z axis
        ear[0].append(height)
        ear[1].append(height)
        ear[2].append(height)

        # TODO U,V are wrong here
        vertex_str += create_vertex_with_normal_str(ear[0], [0.0, 0.0, 1.0], 0.0, 0.0)
        vertex_str += create_vertex_with_normal_str(ear[1], [0.0, 0.0, 1.0], 0.0, 1.0)
        vertex_str += create_vertex_with_normal_str(ear[2], [0.0, 0.0, 1.0], 1.0, 0.0)

        face_str += create_face(vertex_index + 1, vertex_index + 2, vertex_index + 0)

        vertex_index += 3
        face_qty += 1

    return vertex_index, face_qty, vertex_str, face_str


def generate_roof_for_barrier(vertex2d, height, vertex_index):
    face_qty = 0
    vertex_str = ""
    face_str = ""

    # for barrier, the first half vertices are one side, the last half the other side
    index = 0
    vlen = len(vertex2d)
    for v in vertex2d:
        # 2 faces per first half vertex
        v1 = vertex2d[index]
        v2 = vertex2d[index + 1]
        v3 = vertex2d[vlen - 1 - index]
        v1.append(height)
        v2.append(height)
        v3.append(height)
        vertex_str += create_vertex_with_normal_str(v1, [0.0, 0.0, 1.0], 0.0, 0.0)
        vertex_str += create_vertex_with_normal_str(v2, [0.0, 0.0, 1.0], 0.0, 1.0)
        vertex_str += create_vertex_with_normal_str(v3, [0.0, 0.0, 1.0], 1.0, 0.0)

        face_str += create_face(vertex_index + 0, vertex_index + 1, vertex_index + 2)

        vertex_index += 3
        face_qty += 1

        v1 = vertex2d[index + 1]
        v2 = vertex2d[vlen - 1 - index]
        v3 = vertex2d[vlen - 2 - index]
        v1.append(height)
        v2.append(height)
        v3.append(height)
        vertex_str += create_vertex_with_normal_str(v1, [0.0, 0.0, 1.0], 0.0, 0.0)
        vertex_str += create_vertex_with_normal_str(v2, [0.0, 0.0, 1.0], 0.0, 1.0)
        vertex_str += create_vertex_with_normal_str(v3, [0.0, 0.0, 1.0], 1.0, 0.0)

        face_str += create_face(vertex_index + 0, vertex_index + 2, vertex_index + 1)

        vertex_index += 3
        face_qty += 1

        index += 1
        if index >= (vlen / 2) - 1:
            break

    return vertex_index, face_qty, vertex_str, face_str


def get_info_from_input_data(nodes, is_node):
    all_vertex = []
    min_x = 9999999.0
    min_y = 9999999.0
    max_x = -9999999.0
    max_y = -9999999.0

    # First and last nodes are sometimes the same. In this case skip the last node
    if nodes[0] == nodes[-1]:
        nodes.pop()

    for node in nodes:
        if is_node is True:
            x = helper.lat_to_x(node.lat)
            y = helper.lon_to_y(node.lon)
        else:
            x = node[0]
            y = node[1]

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

    centered_vertex = []

    # Make sure vertices are centered on 0,0
    for v in all_vertex:
        # 'Y' axis is inverted on RoR map
        centered_vertex.append([v[0] - center_x, -(v[1] - center_y)])

    # Make sure faces are correctly oriented
    if triangulate.IsClockwise(centered_vertex):
        centered_vertex.reverse()

    return center_x, center_y, max_x - min_x, max_y - min_y, centered_vertex


def create_additional_vertex_for_barrier(vertex):
    # Create vertices "around" each segment
    first_side_vertex = []
    opposite_side_vertex = []

    normal_x = 0.0
    normal_y = 0.0

    for i in range(len(vertex) - 1):
        normal_x = -(vertex[i + 1][1] - vertex[i][1])
        normal_y = vertex[i + 1][0] - vertex[i][0]
        normal_norm = math.sqrt((normal_x * normal_x) + (normal_y * normal_y))
        normal_x = (normal_x / normal_norm) * (config.data["barrier_width"] / 2.0)
        normal_y = (normal_y / normal_norm) * (config.data["barrier_width"] / 2.0)

        first_side_vertex.append([vertex[i][0] + normal_x, vertex[i][1] + normal_y])
        opposite_side_vertex.append([vertex[i][0] - normal_x, vertex[i][1] - normal_y])

    # Use latest normal for last input vertex
    i = len(vertex) - 1

    first_side_vertex.append([vertex[i][0] + normal_x, vertex[i][1] + normal_y])
    opposite_side_vertex.append([vertex[i][0] - normal_x, vertex[i][1] - normal_y])

    first_side_vertex.reverse()
    centered_vertex = opposite_side_vertex + first_side_vertex

    return centered_vertex


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


def generate_mesh_file(submesh, obj_name):
    mesh_str = "<mesh>\n"
    mesh_str += "<submeshes>\n"
    for s in submesh:
        mesh_str += "<submesh material=\"" + s[
            "texture"] + "\" usesharedvertices=\"false\" use32bitindexes=\"false\" operationtype=\"triangle_list\">\n"
        mesh_str += "<faces count=\"" + str(s["face_qty"]) + "\">\n"
        mesh_str += s["face_str"]
        mesh_str += "</faces>\n"
        mesh_str += "<geometry vertexcount=\"" + str(s["vertex_index"]) + "\">\n"
        mesh_str += "<vertexbuffer positions=\"true\" normals=\"true\" texture_coord_dimensions_0=\"float2\" texture_coords=\"1\">"
        mesh_str += s["vertex_str"]
        mesh_str += "</vertexbuffer>\n"
        mesh_str += "</geometry>\n"
        mesh_str += "</submesh>\n"
    mesh_str += "</submeshes>\n"
    mesh_str += "</mesh>\n"

    mesh_file_name = obj_name + ".mesh"
    with open(config.data["work_path"] + mesh_file_name + ".xml", "w") as mesh_file:
        mesh_file.write(mesh_str)

    os.system(
        "OgreXMLConverter " + config.data["work_path"] + obj_name + ".mesh.xml > /dev/null")

    ror_zip_file.add_file(obj_name + ".mesh")
