import config

# https://wiki.openstreetmap.org/wiki/Main_Page
ignored_tags = ["source", "addr:housenumber", "addr:street", "genus:de", "genus:en", "genus:fr", "ref", "check_date:shelter"]

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


def show_stat(original_nodes, modified_nodes):
    global node_total
    global node_empty_qty

    node_total = len(modified_nodes)

    for original_node, node in zip(original_nodes, modified_nodes):
        if len(node.tags) == 0:
            node.tags["empty"] = True

        for tag in ignored_tags:
            if tag in node.tags:
                node.tags.pop(tag)
                original_node.tags.pop(tag)

        if len(node.tags) == 0:
            node.tags["ignored"] = True

        calculate_stats(original_node, node)

    print_stats()


def calculate_stats(original_node, node):
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
        node_ignored = node_ignored + " -- {0}{1}\n".format(node, original_node.tags)
        node_ignored_qty += 1
    elif len(node.tags) == len(original_node.tags):
        node_not_processed = node_not_processed + " -- {0}{1}\n".format(node, node.tags)
        node_not_processed_qty += 1
    elif len(node.tags) > 0:
        node_incomplete = node_incomplete + " -- {0}{1}{2}\n".format(node, node.tags, original_node.tags)
        node_incomplete_qty = node_incomplete_qty + 1
    else:
        node_complete = node_complete + " -- {0}{1}\n".format(node, original_node.tags)
        node_complete_qty += 1


def print_stats():
    with open(config.data["log_path"] + "node_empty.txt", "w") as file:
        file.write(node_empty)
    with open(config.data["log_path"] + "node_ignored.txt", "w") as file:
        file.write(node_ignored)
    with open(config.data["log_path"] + "node_incomplete.txt", "w") as file:
        file.write(node_incomplete)
    with open(config.data["log_path"] + "node_not_processed.txt", "w") as file:
        file.write(node_not_processed)
    with open(config.data["log_path"] + "node_complete.txt", "w") as file:
        file.write(node_complete)

    print("Total nodes  = ", node_total)
    print("Empty nodes  = ", node_empty_qty)
    print("Ignored nodes  = ", node_ignored_qty)
    print("Complete nodes  = ", node_complete_qty)
    print("Incomplete nodes = ", node_incomplete_qty)
    print("Not processed nodes = ", node_not_processed_qty)
    print("")
