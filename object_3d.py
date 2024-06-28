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
                           wall_texture=config.data["wall_texture"], top_texture=config.data["top_texture"],
                           scale=1.0,
                           is_barrier=False, half_barrier=False, wall_texture_generator=None,
                           top_texture_generator=None,
                           roof_shape=None,
                           roof_height=None,
                           barrier_width=config.data["barrier_width"],
                           display_name=None):
    global object_index

    if height is None:
        height = config.data["building_level_height"]
    if z is None:
        z = 0.0

    # Make object on the ground super high to avoid them to "float" when they are near a water coast
    if z == 0.0:
        height += config.data["ground_line"]
        z = -config.data["ground_line"]

    need_roof = False
    if is_roof_shape_supported(roof_shape) and roof_height is not None:
        height -= roof_height
        need_roof = True

    object_index = object_index + 1

    obj_name = "obj" + str(object_index)

    if len(nodes) > 1:
        if hasattr(nodes[0], 'lat'):
            center_x, center_y, width, length, vertex = get_info_from_input_data(nodes, scale=scale, is_node=True,
                                                                                 keep_all_nodes=is_barrier)
        else:
            center_x, center_y, width, length, vertex = get_info_from_input_data(nodes, scale=scale, is_node=False,
                                                                                 keep_all_nodes=is_barrier)

        if is_barrier is True:
            vertex = create_additional_vertex_for_barrier(vertex, half_barrier, barrier_width)
    else:
        center_x, center_y, width, length, vertex = create_vertex_for_pillar(nodes[0])

    wall_vertex_index, wall_face_qty, wall_vertex_str, wall_face_str = generate_wall(vertex, height)
    if wall_vertex_str is None:
        return None

    if wall_texture_generator is not None:
        wall_texture = wall_texture_generator(width, length)
    if top_texture_generator is not None:
        top_texture = top_texture_generator(width, length)

    if wall_texture == top_texture:  # no submeshes with the same texture is allowed, so concatenate wall and top meshes
        if need_roof:
            top_vertex_index, top_face_qty, top_vertex_str, top_face_str = generate_roof(roof_shape, vertex, height,
                                                                                         roof_height,
                                                                                         wall_vertex_index)
        else:
            top_vertex_index, top_face_qty, top_vertex_str, top_face_str = generate_ceiling(vertex, height,
                                                                                            wall_vertex_index,
                                                                                            is_barrier)
        generate_mesh_file(
            [{"vertex_index": top_vertex_index, "face_qty": wall_face_qty + top_face_qty,
              "vertex_str": wall_vertex_str + top_vertex_str,
              "face_str": wall_face_str + top_face_str, "texture": wall_texture}], obj_name)
    else:
        if need_roof:
            top_vertex_index, top_face_qty, top_vertex_str, top_face_str = generate_roof(roof_shape, vertex, height,
                                                                                         roof_height,
                                                                                         0)
        else:
            top_vertex_index, top_face_qty, top_vertex_str, top_face_str = generate_ceiling(vertex, height,
                                                                                            0, is_barrier)
        generate_mesh_file(
            [{"vertex_index": wall_vertex_index, "face_qty": wall_face_qty, "vertex_str": wall_vertex_str,
              "face_str": wall_face_str, "texture": wall_texture},
             {"vertex_index": top_vertex_index, "face_qty": top_face_qty, "vertex_str": top_vertex_str,
              "face_str": top_face_str, "texture": top_texture}], obj_name)

    ror_tobj_file.add_object(center_x, center_y, z, 0.0, 0.0, 0.0, obj_name, display_name)
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


def generate_ceiling(vertex, height, vertex_index, is_barrier):
    if is_barrier is False:
        return generate_ceiling_for_building(vertex, height, vertex_index)
    else:
        return generate_ceiling_for_barrier(vertex, height, vertex_index)


def generate_ceiling_for_building(vertex2d, height, vertex_index):
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


def generate_ceiling_for_barrier(vertex2d, height, vertex_index):
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


def is_roof_shape_supported(shape):
    if shape is None:
        return False
    if shape == "pyramidal":
        return True
    else:
        print("Unsupported roof shape", shape)


def generate_roof(shape, vertex2d, height, roof_height, vertex_index):
    if shape == "pyramidal":
        return generate_roof_pyramidal(vertex2d, height, roof_height, vertex_index)


def generate_roof_pyramidal(vertex2d, height, roof_height, vertex_index):
    face_qty = 0
    vertex_str = ""
    face_str = ""

    # find highest and lowest x and y
    x_high = vertex2d[0][0]
    x_low = vertex2d[0][0]
    y_high = vertex2d[0][1]
    y_low = vertex2d[0][1]
    for v in vertex2d:
        if v[0] > x_high:
            x_high = v[0]
        if v[0] < x_low:
            x_low = v[0]
        if v[1] > y_high:
            y_high = v[1]
        if v[1] < y_low:
            y_low = v[1]

    # calculate top coordinates
    top_x = (x_high + x_low) / 2
    top_y = (y_high + y_low) / 2

    top_vertex = [top_x, top_y, height + roof_height]

    index = 0

    for v in vertex2d:
        v1 = vertex2d[index]
        v2 = vertex2d[(index + 1) % len(vertex2d)]
        v1.append(height)
        v2.append(height)

        norm = helper.calc_norm([v1, v2, top_vertex])

        vertex_str += create_vertex_with_normal_str(v1, [norm[0], norm[1], norm[2]], 0.0, 0.0)
        vertex_str += create_vertex_with_normal_str(v2, [norm[0], norm[1], norm[2]], 0.0, 1.0)
        vertex_str += create_vertex_with_normal_str(top_vertex, [norm[0], norm[1], norm[2]], 1.0, 0.0)

        face_str += create_face(vertex_index + 0, vertex_index + 1, vertex_index + 2)

        vertex_index += 3
        face_qty += 1

        index += 1

    return vertex_index, face_qty, vertex_str, face_str


def get_info_from_input_data(nodes, scale=1.0, is_node=True, keep_all_nodes=False):
    all_vertex = []
    min_x = 9999999.0
    min_y = 9999999.0
    max_x = -9999999.0
    max_y = -9999999.0

    # First and last nodes are sometimes the same. In this case skip the last node unless specified otherwise
    if keep_all_nodes is False:
        if nodes[0] == nodes[-1]:
            nodes.pop()

    for node in nodes:
        if is_node is True:
            x = helper.lon_to_x(node.lon)
            y = helper.lat_to_y(node.lat)
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
        centered_vertex.append([(v[0] - center_x) * scale, (-(v[1] - center_y)) * scale])

    # Make sure faces are correctly oriented
    if triangulate.IsClockwise(centered_vertex):
        centered_vertex.reverse()

    return center_x, center_y, max_x - min_x, max_y - min_y, centered_vertex


def create_additional_vertex_for_barrier(vertex, half_barrier, barrier_width):
    # Create vertices "around" each segment

    loop = False
    if vertex[0] == vertex[-1]:
        # With a looped barrier, we calculate all vertex with intersections.
        # As we need 3 points to calculate an intersection, we had the missing point here.
        # If not looped, we just draw normals of the first and last vertex
        loop = True
        last_vertex = vertex[-2]
        second_vertex = vertex[1]
        vertex.insert(0, last_vertex)  # For intersection on first vertex
        vertex.append(second_vertex)  # for intersection on last vertex

    first_side_vertex = []
    opposite_side_vertex = []

    if loop is False:
        first_vertex_normal = helper.calc_normal(vertex[0], vertex[1], barrier_width / 2.0)
        first_vertex_normal_coord_1 = (vertex[0][0] + first_vertex_normal[0], vertex[0][1] + first_vertex_normal[1])
        first_side_vertex.append(list(first_vertex_normal_coord_1))
        first_vertex_normal_coord_2 = (vertex[0][0] - first_vertex_normal[0], vertex[0][1] - first_vertex_normal[1])
        opposite_side_vertex.append(list(first_vertex_normal_coord_2))

    def calc_normal_coord(origin_vertex, normal, factor):
        return origin_vertex[0] + (factor * normal[0]), origin_vertex[1] + (factor * normal[1])

    def calc_intersection(v1, v2, v3, factor, width):
        start_vertex_normal = helper.calc_normal(v1, v2, width / 2.0)
        start_parallel_p1 = calc_normal_coord(v1, start_vertex_normal, factor)
        start_parallel_p2 = calc_normal_coord(v2, start_vertex_normal, factor)

        end_vertex_normal = helper.calc_normal(v2, v3, width / 2.0)
        end_parallel_p1 = calc_normal_coord(v3, end_vertex_normal, factor)
        end_parallel_p2 = calc_normal_coord(v2, end_vertex_normal, factor)

        return helper.intersect_line((start_parallel_p1, start_parallel_p2), (end_parallel_p1, end_parallel_p2))

    while len(vertex) >= 3:
        # Calculate intersections around current segment and next segment
        start_vertex = vertex.pop(0)
        next_vertex = vertex[0]
        end_vertex = vertex[1]

        # First side
        f = 1.0  # Draw all around the barrier equally
        if half_barrier:
            f = 0.0  # Draw only one side of the barrier
        intersection_1 = calc_intersection(start_vertex, next_vertex, end_vertex, f, barrier_width)

        # second side
        f = -1.0  # Draw all around the barrier equally
        if half_barrier:
            f = -2.0  # Draw only one side of the barrier
        intersection_2 = calc_intersection(start_vertex, next_vertex, end_vertex, f, barrier_width)

        if intersection_1 is None or intersection_2 is None:
            continue
        first_side_vertex.append(list(intersection_1))
        opposite_side_vertex.append(list(intersection_2))

    if loop is False:
        last_vertex_normal = helper.calc_normal(vertex[-2], vertex[-1], barrier_width / 2.0)

        last_vertex_normal_coord_1 = (vertex[-1][0] + last_vertex_normal[0], vertex[-1][1] + last_vertex_normal[1])
        first_side_vertex.append(list(last_vertex_normal_coord_1))

        last_vertex_normal_coord_2 = (vertex[-1][0] - last_vertex_normal[0], vertex[-1][1] - last_vertex_normal[1])
        opposite_side_vertex.append(list(last_vertex_normal_coord_2))

    first_side_vertex.reverse()
    centered_vertex = opposite_side_vertex + first_side_vertex

    return centered_vertex


def create_vertex_for_pillar(node):
    x = helper.lon_to_x(node.lon)
    y = helper.lat_to_y(node.lat)

    length = config.data["barrier_width"] / 2.0

    vertex = [[length, length], [length, -length],
              [-length, -length], [-length, length]]
    return x, y, config.data["barrier_width"], config.data["barrier_width"], vertex


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

    ror_zip_file.add_to_zip_file_list(obj_name + ".mesh")
