import math
import bbox
import numpy
from math import atan2, degrees
import ogre_map_height

EARTH_RADIUS = 6371000


# Return distance (in meters) between 2 points described by their latitude/longitude
def lat_lon_to_distance(lat1, lat2, lon1, lon2):
    a = math.sin(math.radians(lat1)) * math.sin(math.radians(lat2)) + math.cos(math.radians(lat1)) * math.cos(
        math.radians(lat2)) * math.cos(math.radians(lon2 - lon1))
    if a > 1.0:
        a = 1.0
    if a < -1.0:
        a = -1.0

    return math.acos(a) * EARTH_RADIUS


# Return X from latitude
def lat_to_y(lat):
    if float(lat) > bbox.coord["north"]:
        return -lat_lon_to_distance(float(lat), bbox.coord["north"], bbox.coord["east"], bbox.coord["east"])
    else:
        return lat_lon_to_distance(float(lat), bbox.coord["north"], bbox.coord["east"], bbox.coord["east"])


# Return Y from longitude
def lon_to_x(lon):
    if float(lon) > bbox.coord["west"]:
        return lat_lon_to_distance(bbox.coord["north"], bbox.coord["north"], bbox.coord["west"], float(lon))
    else:
        return -lat_lon_to_distance(bbox.coord["north"], bbox.coord["north"], bbox.coord["west"], float(lon))


# Get an array of 3 vertices
# A vertex is an array of 3 values (x,y,z)
# Return an array of 3 values
def calc_norm(triangle_vertices):
    ux, uy, uz = [triangle_vertices[1][0] - triangle_vertices[0][0], triangle_vertices[1][1] - triangle_vertices[0][1],
                  triangle_vertices[1][2] - triangle_vertices[0][2]]  # first vector
    vx, vy, vz = [triangle_vertices[2][0] - triangle_vertices[0][0], triangle_vertices[2][1] - triangle_vertices[0][1],
                  triangle_vertices[2][2] - triangle_vertices[0][2]]  # sec vector

    cross = [uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx]  # cross product

    # Normalize
    return cross / numpy.linalg.norm(cross)


def calc_normal(p1, p2, external_norm=1.0):
    p1x, p1y = p1
    p2x, p2y = p2
    normal_x = -(p2y - p1y)
    normal_y = p2x - p1x
    normal_norm = math.sqrt((normal_x * normal_x) + (normal_y * normal_y))
    return (normal_x / normal_norm) * external_norm, (normal_y / normal_norm) * external_norm


def angle_between(v1, v2, v3):
    x1, y1 = v1
    x2, y2 = v2
    x3, y3 = v3
    deg1 = degrees(atan2(y1 - y2, x1 - x2))
    deg2 = degrees(atan2(y3 - y2, x3 - x2))

    angle = deg2 - deg1

    if angle > 180.0:
        angle = -360.0 + angle
    elif angle < -180.0:
        angle = 360.0 + angle

    return angle


# intersection between segment(p1, p2) and segment(p3, p4)
def intersect_segment(p1, p2, p3, p4):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4
    denom = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
    if denom == 0:  # parallel
        return None
    ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denom
    if ua < 0 or ua > 1:  # out of range
        return None
    ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denom
    if ub < 0 or ub > 1:  # out of range
        return None
    x = x1 + ua * (x2 - x1)
    y = y1 + ua * (y2 - y1)
    return x, y


# intersection between line(p1, p2) and line(p3, p4)
def intersect_line(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0: # Parallel
        return None

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return x, y


def intersect_between_all_direction(p1, p2):
    p3 = bbox.coordXY["west"], bbox.coordXY["north"]
    p4 = bbox.coordXY["east"], bbox.coordXY["north"]
    intersection_coord = intersect_segment(p1, p2, p3, p4)
    if intersection_coord is not None:
        return intersection_coord, "north"

    p3 = bbox.coordXY["west"], bbox.coordXY["south"]
    p4 = bbox.coordXY["east"], bbox.coordXY["south"]
    intersection_coord = intersect_segment(p1, p2, p3, p4)
    if intersection_coord is not None:
        return intersection_coord, "south"

    p3 = bbox.coordXY["west"], bbox.coordXY["north"]
    p4 = bbox.coordXY["west"], bbox.coordXY["south"]
    intersection_coord = intersect_segment(p1, p2, p3, p4)
    if intersection_coord is not None:
        return intersection_coord, "west"

    p3 = bbox.coordXY["east"], bbox.coordXY["north"]
    p4 = bbox.coordXY["east"], bbox.coordXY["south"]
    intersection_coord = intersect_segment(p1, p2, p3, p4)
    if intersection_coord is not None:
        return intersection_coord, "east"

    return None, None


def is_inside_map(p1):
    x, y = p1
    return bbox.coordXY["west"] < x < bbox.coordXY["east"] and bbox.coordXY["north"] < y < bbox.coordXY["south"]


def is_power_of_2(n):
    return (math.log(n) / math.log(2)).is_integer()


def node_to_map_coord(all_node):
    all_coord = []

    # First and last nodes are sometimes the same. In this case skip the last node
    if all_node[0] == all_node[-1]:
        all_node.pop()

    for node in all_node:
        x = lon_to_x(node.lon) * ogre_map_height.MAP_HEIGHT_SIZE_FACTOR
        y = lat_to_y(node.lat) * ogre_map_height.MAP_HEIGHT_SIZE_FACTOR

        all_coord.append(x)
        all_coord.append(y)

    return all_coord
