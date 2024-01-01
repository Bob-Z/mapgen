import helper
import ror_tobj_file
import ror_odef_file
import config
import bbox
import object_3d

# https://wiki.openstreetmap.org/wiki/Main_Page
ignored_tags = ["source", "access", "description", "description:en", "description:de", "description:fr", "old_ref"]
ignored_tags_value = []
ignored_relations = ["admin_level"]

relation_total = 0
relation_empty = ""
relation_empty_qty = 0
relation_incomplete = ""
relation_incomplete_qty = 0
relation_ignored = ""
relation_ignored_qty = 0
relation_complete = ""
relation_complete_qty = 0
relation_not_processed = ""
relation_not_processed_qty = 0


def show_stat(original_relations, modified_relations):
    global relation_total

    relation_total = len(modified_relations)

    for original_rel, rel in zip(original_relations, modified_relations):
        if len(rel.tags) == 0:
            rel.tags["empty"] = True

        for tag in ignored_relations:
            if tag in rel.tags:
                rel.tags["ignored"] = True

        for tag_value in ignored_tags_value:
            if tag_value[0] in rel.tags:
                if rel.tags[tag_value[0]] == tag_value[1]:
                    rel.tags["ignored"] = True

        for tag in ignored_tags:
            if tag in rel.tags:
                rel.tags.pop(tag)
                original_rel.tags.pop(tag)

        calculate_stats(original_rel, rel)

    print_stats()


def calculate_stats(original_rel, rel):
    global relation_empty
    global relation_empty_qty
    global relation_not_processed
    global relation_not_processed_qty
    global relation_incomplete
    global relation_incomplete_qty
    global relation_complete
    global relation_complete_qty
    global relation_ignored
    global relation_ignored_qty

    if "empty" in rel.tags:
        relation_empty = relation_empty + " -- {0}\n".format(rel)
        relation_empty_qty += 1
    elif "ignored" in rel.tags:
        relation_ignored = relation_ignored + " -- {0}{1}\n".format(rel, original_rel.tags)
        relation_ignored_qty += 1
    elif len(rel.tags) == len(original_rel.tags):
        relation_not_processed = relation_not_processed + " -- {0}{1}\n".format(rel, rel.tags)
        relation_not_processed_qty += 1
    elif len(rel.tags) > 0:
        relation_incomplete = relation_incomplete + " -- {0}{1}{2}\n".format(rel, rel.tags, original_rel.tags)
        relation_incomplete_qty += 1
    else:
        relation_complete = relation_complete + " -- {0}{1}\n".format(rel, original_rel.tags)
        relation_complete_qty += 1


def print_stats():
    with open(config.data["log_path"] + "relation_empty.txt", "w") as file:
        file.write(relation_empty)
    with open(config.data["log_path"] + "relation_ignored.txt", "w") as file:
        file.write(relation_ignored)
    with open(config.data["log_path"] + "relation_incomplete.txt", "w") as file:
        file.write(relation_incomplete)
    with open(config.data["log_path"] + "relation_not_processed.txt", "w") as file:
        file.write(relation_not_processed)
    with open(config.data["log_path"] + "relation_complete.txt", "w") as file:
        file.write(relation_complete)

    print("Total relations  = ", relation_total)
    print("Empty relations  = ", relation_empty_qty)
    print("Ignored relations  = ", relation_ignored_qty)
    print("Complete relations  = ", relation_complete_qty)
    print("Incomplete relations = ", relation_incomplete_qty)
    print("Not processed relations = ", relation_not_processed_qty)
    print("")
