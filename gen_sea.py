import gvar
import object_3d
import config
import bbox
import helper


def process(osm_data):
    print("Generating sea")
    for way in osm_data.ways:
        if "natural" in way.tags:
            if way.tags["natural"] == "coastline":
                build_coastline(osm_data.ways)
                way.tags.pop("natural")
                break


def is_after_clock_wise(coord1, coord2, direction):
    if direction == "north":
        if coord1[1] > coord2[1]:
            return True

    if direction == "south":
        if coord1[1] < coord2[1]:
            return True

    if direction == "west":
        if coord1[0] > coord2[0]:
            return True

    if direction == "east":
        if coord1[0] < coord2[0]:
            return True

    return False


def get_direction_corner(direction):
    if direction == "north":
        return [bbox.coordXY["north"], bbox.coordXY["east"]]
    if direction == "south":
        return [bbox.coordXY["south"], bbox.coordXY["west"]]
    if direction == "west":
        return [bbox.coordXY["north"], bbox.coordXY["west"]]
    if direction == "east":
        return [bbox.coordXY["south"], bbox.coordXY["east"]]


def get_next_direction_clock_wise(direction):
    if direction == "north":
        return "east"
    if direction == "south":
        return "west"
    if direction == "west":
        return "north"
    if direction == "east":
        return "south"


def build_coastline(way):
    all_coastline = []
    for w in way:
        if "natural" in w.tags:
            if w.tags["natural"] == "coastline":
                all_coastline.append(w.nodes)

    print(len(all_coastline), "coastlines")

    # Generate complete coastline from fragmented coastlines
    complete_coastline = []
    while len(all_coastline) > 0:
        found = True
        base_coastline = all_coastline.pop()
        while found is True:
            found = False
            index = 0
            for c in all_coastline:
                if c[0] == base_coastline[-1]:
                    base_coastline.pop()
                    base_coastline = base_coastline + c
                    all_coastline.pop(index)
                    found = True
                    break
                if c[-1] == base_coastline[0]:
                    c.pop()
                    base_coastline = c + base_coastline
                    all_coastline.pop(index)
                    found = True
                    break

                index += 1

        base_coastline_xy = []
        for n in base_coastline:
            base_coastline_xy.append([helper.lat_to_x(n.lat), helper.lon_to_y(n.lon)])

        complete_coastline.append(base_coastline_xy)

    print(str(len(complete_coastline)) + " complete coastlines")

    polygon_list = []

    # Generate entry/exit list
    entry_exit_list = []
    item_id = 0

    for coastline in complete_coastline:
        prev_coord = None
        is_inside_map = False
        entry_exit_item = {}

        # Case where all coastline is inside the map:
        if helper.is_inside_map(coastline[0]):
            polygon_list.append(coastline)
            continue
        else:
            for coord in coastline:
                if prev_coord is not None:
                    intersection, cut_direction = helper.intersect_between_all_direction((prev_coord[0], prev_coord[1]),
                                                                                         (coord[0], coord[1]))
                    if is_inside_map is False:
                        if intersection is not None:
                            is_inside_map = True

                            entry_exit_item["coord"] = [intersection, coord]
                            entry_exit_item["entry_direction"] = cut_direction
                    else:
                        if intersection is not None:
                            entry_exit_item["coord"].append(intersection)

                            is_inside_map = False
                            entry_exit_item["exit_direction"] = cut_direction
                            entry_exit_item["id"] = item_id
                            entry_exit_item["entry_done"] = False
                            entry_exit_item["exit_done"] = False

                            item_id += 1

                            entry_exit_list.append(entry_exit_item)
                            entry_exit_item = {}
                        else:
                            entry_exit_item["coord"].append(coord)

                prev_coord = coord

            # Find an exit following an entry clockwise (because ground is left side of the coastline)
            no_more_entry = False
            while no_more_entry is False:
                # find not processed entry
                no_more_entry = True
                for item in entry_exit_list:
                    if item["entry_done"] is False:
                        no_more_entry = False
                        item["entry_done"] = True
                        polygon = item["coord"].copy()
                        direction = item["entry_direction"]
                        entry_coord = item["coord"][0]
                        exit_coord = None
                        found_item = None
                        polygon_complete = False
                        start_id = item["id"]

                        while polygon_complete is False:
                            for i in entry_exit_list:
                                # both entry and exit are on the same direction
                                if i["exit_done"] is False:
                                    if i["exit_direction"] == direction:
                                        if is_after_clock_wise(i["coord"][-1], entry_coord, direction) is True:
                                            if exit_coord is not None:
                                                if is_after_clock_wise(exit_coord, i["coord"][-1], direction) is True:
                                                    exit_coord = i["coord"][-1]
                                                    found_item = i
                                                    continue
                                                else:
                                                    # this exit is "after" a previously found exit, skip this item
                                                    continue
                                            else:
                                                # First exit found
                                                exit_coord = i["coord"][-1]
                                                found_item = i
                                                continue

                            # No item found on this direction, add direction's corner's coordinates and try with the next direction
                            if found_item is None:
                                entry_coord = get_direction_corner(direction)
                                polygon.insert(0, entry_coord)
                                direction = get_next_direction_clock_wise(direction)
                            else:
                                found_item["exit_done"] = True
                                if found_item["id"] == start_id:
                                    # Polygon is complete
                                    polygon_list.append(polygon)
                                    polygon_complete = True
                                else:
                                    # loop again with the item's entry found
                                    found_item["entry_done"] = True
                                    polygon = found_item["coord"] + polygon
                                    direction = found_item["entry_direction"]
                                    entry_coord = found_item["coord"][0]
                                    found_item["entry_done"] = True
                                    exit_coord = None
                                    found_item = None

    for polygon in polygon_list:
        object_3d.create_all_object_file(polygon, height=gvar.GROUND_LEVEL, z=-gvar.GROUND_LEVEL, wall_texture="mapgen_beige",
                                         roof_texture="mapgen_beige")
