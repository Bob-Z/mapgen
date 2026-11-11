import helper

# Bounding box in latitude, longitude: {"north": north, "south": south, "west": west, "east": east}
direction = ["north", "east", "south", "west"]
coord = []
coordXY = []
bounding_box = ""


def init(center, size):
    map_coord = calculate_bbox(center, size)
    global coord
    coord = map_coord
    global coordXY
    coordXY = {"north": helper.lat_to_y(coord["north"]), "south": helper.lat_to_y(coord["south"]),
               "west": helper.lon_to_x(coord["west"]),
               "east": helper.lon_to_x(coord["east"])}
    global bounding_box
    bounding_box = str(coord["south"]) + "," + str(coord["west"]) + "," + str(
        coord["north"]) + "," + str(coord["east"])



def calculate_bbox(center, size):
    center_lat = float(center[0])
    center_lon = float(center[1])
    meter_by_degree_of_latitude = helper.lat_lon_to_distance(center_lat, center_lat + 1.0, center_lon, center_lon)
    meter_by_degree_of_longitude = helper.lat_lon_to_distance(center_lat, center_lat, center_lon, center_lon + 1.0)

    north = center_lat + (size / 2.0) / meter_by_degree_of_latitude
    south = center_lat - (size / 2.0) / meter_by_degree_of_latitude
    west = center_lon + (size / 2.0) / meter_by_degree_of_longitude
    east = center_lon - (size / 2.0) / meter_by_degree_of_longitude

    if north < south:
        t = south
        south = north
        north = t
    if west > east:
        t = west
        west = east
        east = t

    return {"north": north, "south": south, "west": west, "east": east}
    # print("Bounding box:", bbox.coord, bbox.coordXY)
