import helper
import ror_tobj_file
import ror_odef_file
import ogre_mesh
import gvar
import bbox

# https://wiki.openstreetmap.org/wiki/Main_Page
ignored_tags = ["source", "access", "description", "description:en", "description:de", "description:fr", "old_ref"]
ignored_tags_value = [["landuse", "residential"], ["landuse", "retail"], ["railway", "razed"]]
ignored_ways = ["admin_level"]

way_total = 0
way_empty = ""
way_empty_qty = 0
way_incomplete = ""
way_incomplete_qty = 0
way_ignored = ""
way_ignored_qty = 0
way_complete = ""
way_complete_qty = 0
way_not_processed = ""
way_not_processed_qty = 0


def process(result):
    global way_total

    way_total = len(result.ways)
    way_qty = 0

    build_coastline(result.ways)

    for way in result.ways:
        way_qty += 1
        print("processing way " + str(way_qty) + "/" + str(way_total), end='\r', flush=True)

        if len(way.tags) == 0:
            way.tags["empty"] = True

        original_tags = way.tags.copy()

        for tag in ignored_ways:
            if tag in way.tags:
                way.tags["ignored"] = True

        for tag_value in ignored_tags_value:
            if tag_value[0] in way.tags:
                if way.tags[tag_value[0]] == tag_value[1]:
                    way.tags["ignored"] = True

        for tag in ignored_tags:
            if tag in way.tags:
                way.tags.pop(tag)

        if "highway" in way.tags:
            ror_tobj_file.create_road(way)
        if "building" in way.tags:
            create_object(way)
            way.tags.pop("building")
        if "disused:building" in way.tags:
            create_object(way)
            way.tags.pop("disused:building")
        if "demolished:building" in way.tags:
            create_object(way)
            way.tags.pop("demolished:building")
        if "landuse" in way.tags:
            create_object(way)
        if "leisure" in way.tags:
            create_object(way)
        if "barrier" in way.tags:
            create_object(way)
        if "amenity" in way.tags:
            create_object(way)
        if "waterway" in way.tags:
            create_object(way)
        if "natural" in way.tags:
            create_object(way)

        calculate_stats(way, original_tags)

    print("")
    print("")
    print_stats()


def create_object(way):
    new_object = ogre_mesh.create_mesh(way)
    if new_object is not None:
        ror_tobj_file.add_object(new_object)
        ror_odef_file.create_file(new_object)


def calculate_stats(way, original_tags):
    global way_empty
    global way_empty_qty
    global way_not_processed
    global way_not_processed_qty
    global way_incomplete
    global way_incomplete_qty
    global way_complete
    global way_complete_qty
    global way_ignored
    global way_ignored_qty

    if "empty" in way.tags:
        way_empty = way_empty + " -- {0}\n".format(way)
        way_empty_qty += 1
    elif "ignored" in way.tags:
        way_ignored = way_ignored + " -- {0}{1}\n".format(way, original_tags)
        way_ignored_qty += 1
    elif len(way.tags) == len(original_tags):
        way_not_processed = way_not_processed + " -- {0}{1}\n".format(way, way.tags)
        way_not_processed_qty += 1
    elif len(way.tags) > 0:
        way_incomplete = way_incomplete + " -- {0}{1}{2}\n".format(way, way.tags, original_tags)
        way_incomplete_qty += 1
    else:
        way_complete = way_complete + " -- {0}{1}\n".format(way, original_tags)
        way_complete_qty += 1


def print_stats():
    with open(gvar.LOG_PATH + "way_empty.txt", "w") as file:
        file.write(way_empty)
    with open(gvar.LOG_PATH + "way_ignored.txt", "w") as file:
        file.write(way_ignored)
    with open(gvar.LOG_PATH + "way_incomplete.txt", "w") as file:
        file.write(way_incomplete)
    with open(gvar.LOG_PATH + "way_not_processed.txt", "w") as file:
        file.write(way_not_processed)
    with open(gvar.LOG_PATH + "way_complete.txt", "w") as file:
        file.write(way_complete)

    print("Total ways  = ", way_total)
    print("Empty ways  = ", way_empty_qty)
    print("Ignored ways  = ", way_ignored_qty)
    print("Complete ways  = ", way_complete_qty)
    print("Incomplete ways = ", way_incomplete_qty)
    print("Not processed ways = ", way_not_processed_qty)
    print("")


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

        base_coastlineXY = []
        for n in base_coastline:
            base_coastlineXY.append([helper.lat_to_x(n.lat), helper.lon_to_y(n.lon)])

        complete_coastline.append(base_coastlineXY)

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

    # FIXME remove Z axis
    for polygon in polygon_list:
        for p in polygon:
            if len(p) == 2:
                p.append(0.0)

    ground_name_index = 0
    for polygon in polygon_list:
        wall_vertex_index, wall_face_qty, wall_vertex_str, wall_face_str = ogre_mesh.generate_wall(polygon)
        if wall_vertex_str is None:
            return

        building_name = "ground_" + str(ground_name_index)
        ogre_mesh.building_name = building_name
        ground_name_index += 1
        roof_vertex_index, roof_face_qty, roof_vertex_str, roof_face_str = ogre_mesh.generate_roof(polygon,
                                                                                                   wall_vertex_index)
        ogre_mesh.generate_mesh_file(
            [{"vertex_index": roof_vertex_index, "face_qty": wall_face_qty + roof_face_qty,
              "vertex_str": wall_vertex_str + roof_vertex_str,
              "face_str": wall_face_str + roof_face_str, "texture": "mapgen_beige"}])

        new_object = {"x": 0.0,
                      "y": 0.0, "z": 0.0, "rx": 180.0, "ry": 0.0, "rz": 0.0,  # FIXME why 180 ?
                      "name": building_name, "collision": True}
        ror_tobj_file.add_object(new_object)
        ror_odef_file.create_file(new_object)
