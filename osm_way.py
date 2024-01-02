import helper
import ror_tobj_file
import ror_odef_file
import config
import bbox
import object_3d

# https://wiki.openstreetmap.org/wiki/Main_Page
ignored_tags = ["source", "access", "description", "description:en", "description:de", "description:fr", "old_ref",
                "addr:city", "addr:state"]
ignored_tags_value = [["landuse", "residential"], ["landuse", "retail"], ["railway", "razed"]]
ignored_ways = ["admin_level", "disused:admin_level"]

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


def filter_ignored(modified_ways):
    for way in modified_ways:
        if len(way.tags) == 0:
            way.tags["empty"] = True

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


def show_stat(original_ways, modified_ways):
    global way_total

    way_total = len(modified_ways)

    for original_way, way in zip(original_ways, modified_ways):
        calculate_stats(original_way, way)

    print_stats()


def calculate_stats(original_way, way):
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
        way_ignored = way_ignored + " -- {0}{1}\n".format(way, original_way.tags)
        way_ignored_qty += 1
    elif len(way.tags) == len(original_way.tags):
        way_not_processed = way_not_processed + " -- {0}{1}\n".format(way, way.tags)
        way_not_processed_qty += 1
    elif len(way.tags) > 0:
        way_incomplete = way_incomplete + " -- {0}{1}{2}\n".format(way, way.tags, original_way.tags)
        way_incomplete_qty += 1
    else:
        way_complete = way_complete + " -- {0}{1}\n".format(way, original_way.tags)
        way_complete_qty += 1


def print_stats():
    with open(config.data["log_path"] + "way_empty.txt", "w") as file:
        file.write(way_empty)
    with open(config.data["log_path"] + "way_ignored.txt", "w") as file:
        file.write(way_ignored)
    with open(config.data["log_path"] + "way_incomplete.txt", "w") as file:
        file.write(way_incomplete)
    with open(config.data["log_path"] + "way_not_processed.txt", "w") as file:
        file.write(way_not_processed)
    with open(config.data["log_path"] + "way_complete.txt", "w") as file:
        file.write(way_complete)

    print("Total ways  = ", way_total)
    print("Empty ways  = ", way_empty_qty)
    print("Ignored ways  = ", way_ignored_qty)
    print("Complete ways  = ", way_complete_qty)
    print("Incomplete ways = ", way_incomplete_qty)
    print("Not processed ways = ", way_not_processed_qty)
    print("")
