import ror_tobj_file
import ror_odef_file
import ogre_mesh
import gvar

# https://wiki.openstreetmap.org/wiki/Main_Page
ignored_tags = ["source", "access", "description", "description:en", "description:de", "description:fr"]
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

    for way in result.ways:
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
        if "surface" in way.tags:
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
