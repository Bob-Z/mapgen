import config

# https://wiki.openstreetmap.org/wiki/Main_Page
ignored_tags = ["access", "addr:city", "addr:hamlet", "addr:housenumber", "addr:postcode", "addr:state", "addr:street",
                "check_date",
                "check_date:shelter", "description",
                "description:en", "description:de", "description:fr", "fixme", "genus:de", "genus:en", "genus:fr",
                "intermittent",
                "name", "old_name", "old_ref", "ref", "source"]

ignored_tags_value = [["landuse", "construction"], ["landuse", "industrial"], ["landuse", "residential"], ["landuse", "retail"], ["railway", "razed"]]
ignored = ["admin_level", "boundary", "disused:admin_level", "disused:boundary", "disused:route"]

entity_total = 0
entity_empty = ""
entity_empty_qty = 0
entity_incomplete = ""
entity_incomplete_qty = 0
entity_ignored = ""
entity_ignored_qty = 0
entity_complete = ""
entity_complete_qty = 0
entity_not_processed = ""
entity_not_processed_qty = 0


def filter_ignored(modified_entity):
    for entity in modified_entity:
        if len(entity.tags) == 0:
            entity.tags["empty"] = True

        for tag in ignored:
            if tag in entity.tags:
                entity.tags["ignored"] = True

        for tag_value in ignored_tags_value:
            if tag_value[0] in entity.tags:
                if entity.tags[tag_value[0]] == tag_value[1]:
                    entity.tags["ignored"] = True

        for tag in ignored_tags:
            if tag in entity.tags:
                entity.tags.pop(tag)


def show_stat(name, original_entity, modified_entity):
    global entity_total
    global entity_empty
    global entity_empty_qty
    global entity_not_processed
    global entity_not_processed_qty
    global entity_incomplete
    global entity_incomplete_qty
    global entity_complete
    global entity_complete_qty
    global entity_ignored
    global entity_ignored_qty

    entity_total = len(modified_entity)
    entity_empty = ""
    entity_empty_qty = 0
    entity_incomplete = ""
    entity_incomplete_qty = 0
    entity_ignored = ""
    entity_ignored_qty = 0
    entity_complete = ""
    entity_complete_qty = 0
    entity_not_processed = ""
    entity_not_processed_qty = 0

    for original_rel, rel in zip(original_entity, modified_entity):
        calculate_stats(original_rel, rel)

    print_stats(name)


def calculate_stats(original_entity, entity):
    global entity_empty
    global entity_empty_qty
    global entity_not_processed
    global entity_not_processed_qty
    global entity_incomplete
    global entity_incomplete_qty
    global entity_complete
    global entity_complete_qty
    global entity_ignored
    global entity_ignored_qty

    original_without_ignored_tags = original_entity.tags.copy()
    for tag in ignored_tags:
        if tag in original_without_ignored_tags:
            original_without_ignored_tags.pop(tag)

    if "empty" in entity.tags:
        entity_empty = entity_empty + "{0}\n".format(entity)
        entity_empty_qty += 1
    elif "ignored" in entity.tags:
        entity_ignored = entity_ignored + "{0} {1}\n".format(original_entity.tags, entity)
        entity_ignored_qty += 1
    elif len(entity.tags) == len(original_without_ignored_tags):
        entity_not_processed = entity_not_processed + "{0} {1}\n".format(original_entity.tags, entity)
        entity_not_processed_qty += 1
    elif len(entity.tags) > 0:
        entity_incomplete = entity_incomplete + "{0} ||| {1} {2}\n".format(entity.tags, original_entity.tags, entity)
        entity_incomplete_qty += 1
    else:
        entity_complete = entity_complete + "{0} {1}\n".format(original_entity.tags, entity)
        entity_complete_qty += 1


def print_stats(name):
    with open(config.data["log_path"] + name + "_empty.txt", "w") as file:
        file.write(entity_empty)
    with open(config.data["log_path"] + name + "_ignored.txt", "w") as file:
        file.write(entity_ignored)
    with open(config.data["log_path"] + name + "_incomplete.txt", "w") as file:
        file.write(entity_incomplete)
    with open(config.data["log_path"] + name + "_not_processed.txt", "w") as file:
        file.write(entity_not_processed)
    with open(config.data["log_path"] + name + "_complete.txt", "w") as file:
        file.write(entity_complete)

    print("")
    print("Total ", name, " = ", entity_total)
    print("Empty ", name, "  = ", entity_empty_qty)
    print("Ignored ", name, "  = ", entity_ignored_qty)
    print("Complete ", name, "  = ", entity_complete_qty)
    print("Incomplete ", name, " = ", entity_incomplete_qty)
    print("Not processed ", name, " = ", entity_not_processed_qty)
