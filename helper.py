import math
import bbox
import numpy

EARTH_RADIUS = 6371000


# Return distance (in meters) between 2 points described by their latitude/longitude
def lat_lon_to_distance(lat1, lat2, lon1, lon2):
    return math.acos(
        math.sin(math.radians(lat1)) * math.sin(math.radians(lat2)) + math.cos(math.radians(lat1)) * math.cos(
            math.radians(lat2)) * math.cos(math.radians(lon2 - lon1))) * EARTH_RADIUS


# Return X from latitude
def lat_to_x(lat):
    return lat_lon_to_distance(float(lat), bbox.coord["south"], bbox.coord["east"], bbox.coord["east"])


# Return Y from longitude
def lon_to_y(lon):
    return lat_lon_to_distance(bbox.coord["north"], bbox.coord["north"], bbox.coord["east"], float(lon))


# Get an array of 3 vertices
# A vertex is an array of 3 values (x,y,z)
# Return an array of 3 values
def calc_norm(vertex):
    ux, uy, uz = [vertex[1][0] - vertex[0][0], vertex[1][1] - vertex[0][1], vertex[1][2] - vertex[0][2]]  # first vector
    vx, vy, vz = [vertex[2][0] - vertex[0][0], vertex[2][1] - vertex[0][1], vertex[2][2] - vertex[0][2]]  # sec vector

    cross = [uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx]  # cross product

    # Normalize
    return cross / numpy.linalg.norm(cross)


