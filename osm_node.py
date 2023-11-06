import helper
import ror_tobj_file
import random
import gvar

# https://wiki.openstreetmap.org/wiki/Main_Page
ignored_tags = ["source", "addr:housenumber", "addr:street", "genus:de", "genus:en", "genus:fr", "ref"]
# Traffic signals are managed when processing road
ignored_tags_value = [["highway", "traffic_signals"]]

node_total = 0
node_incomplete = ""
node_incomplete_qty = 0
node_empty = ""
node_empty_qty = 0
node_ignored = ""
node_ignored_qty = 0
node_complete = ""
node_complete_qty = 0
node_not_processed = ""
node_not_processed_qty = 0


def process(result):
    global node_total
    global node_empty_qty

    node_total = len(result.nodes)
    node_qty = 0
    for node in result.nodes:
        node_qty += 1
        print("processing node " + str(node_qty) + "/" + str(node_total), end='\r', flush=True)

        if len(node.tags) == 0:
            node.tags["empty"] = True

        original_tags = node.tags.copy()

        for tag in ignored_tags:
            if tag in node.tags:
                node.tags.pop(tag)

        if len(node.tags) == 0:
            node.tags["ignored"] = True

        for tag_value in ignored_tags_value:
            if tag_value[0] in node.tags:
                if node.tags[tag_value[0]] == tag_value[1]:
                    node.tags["ignored"] = True

        if "natural" in node.tags:
            if node.tags["natural"] == "tree":
                add_object(node, "tree1", rx=90.0, ry=float(random.randint(0, 359)))
                node.tags.pop("natural")

        calculate_stats(node, original_tags)
        node.tags = original_tags

    print("")
    print("")
    print_stats()


def add_object(node, name, rx=0.0, ry=0.0, rz=0.0):
    obj = {"x": helper.lat_to_x(node.lat), "y": helper.lon_to_y(node.lon), "z": 0.0, "rx": rx, "ry": ry, "rz": rz,
           "name": name}
    ror_tobj_file.add_object(obj)


def calculate_stats(node, original_tags):
    global node_empty
    global node_empty_qty
    global node_not_processed
    global node_not_processed_qty
    global node_incomplete
    global node_incomplete_qty
    global node_complete
    global node_complete_qty
    global node_ignored
    global node_ignored_qty
    global node_empty_qty

    if "empty" in node.tags:
        node_empty = node_empty + " -- {0}\n".format(node)
        node_empty_qty += 1
    elif "ignored" in node.tags:
        node_ignored = node_ignored + " -- {0}{1}\n".format(node, original_tags)
        node_ignored_qty += 1
    elif len(node.tags) == len(original_tags):
        node_not_processed = node_not_processed + " -- {0}{1}\n".format(node, node.tags)
        node_not_processed_qty += 1
    elif len(node.tags) > 0:
        node_incomplete = node_incomplete + " -- {0}{1}{2}\n".format(node, node.tags, original_tags)
        node_incomplete_qty = node_incomplete_qty + 1
    else:
        node_complete = node_complete + " -- {0}{1}\n".format(node, original_tags)
        node_complete_qty += 1


def print_stats():
    with open(gvar.LOG_PATH + "node_empty.txt", "w") as file:
        file.write(node_empty)
    with open(gvar.LOG_PATH + "node_ignored.txt", "w") as file:
        file.write(node_ignored)
    with open(gvar.LOG_PATH + "node_incomplete.txt", "w") as file:
        file.write(node_incomplete)
    with open(gvar.LOG_PATH + "node_not_processed.txt", "w") as file:
        file.write(node_not_processed)
    with open(gvar.LOG_PATH + "node_complete.txt", "w") as file:
        file.write(node_complete)

    print("Total nodes  = ", node_total)
    print("Empty nodes  = ", node_empty_qty)
    print("Ignored nodes  = ", node_ignored_qty)
    print("Complete nodes  = ", node_complete_qty)
    print("Incomplete nodes = ", node_incomplete_qty)
    print("Not processed nodes = ", node_not_processed_qty)
    print("")
