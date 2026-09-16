import helper

# Bounding box in latitude, longitude: {"north": north, "south": south, "west": west, "east": east}
direction = ["north", "east", "south", "west"]
coord = []
coordXY = []


def init(center, size):
    map_coord = calculate_bbox(center, size)
    global coord
    coord = map_coord
    global coordXY
    coordXY = {"north": helper.lat_to_y(coord["north"]), "south": helper.lat_to_y(coord["south"]),
               "west": helper.lon_to_x(coord["west"]),
               "east": helper.lon_to_x(coord["east"])}


def calculate_bbox(center, size):
    center_lat = float(center[0])
    center_lon = float(center[1])
    meter_by_decimal_latitude = helper.lat_lon_to_distance(center_lat, center_lat + 0.1, center_lon, center_lon)
    meter_by_decimal_longitude = helper.lat_lon_to_distance(center_lat, center_lat, center_lon, center_lon + 0.1)

    north = center_lat + (size / 2.0) / meter_by_decimal_latitude * 0.1
    south = center_lat - (size / 2.0) / meter_by_decimal_latitude * 0.1
    west = center_lon + (size / 2.0) / meter_by_decimal_longitude * 0.1
    east = center_lon - (size / 2.0) / meter_by_decimal_longitude * 0.1

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
