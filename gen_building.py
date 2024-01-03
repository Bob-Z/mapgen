import object_3d
import config
import osm

build_tag_value = [["type", "building"]]
build_tag = ["building:part", "building"]
negative_tag_value = [["amenity", "shelter"], ["building", "rocket"]]
# Exception for rocket for Bocca Chica


def process(osm_data):
    print("Generating buildings")
    for way in osm_data.ways:
        build_from_way(way)

    # Negative tags first

    for rel in osm_data.relations:
        found = False
        for tag_value in build_tag_value:
            if tag_value[0] in rel.tags:
                if rel.tags[tag_value[0]] == tag_value[1]:
                    if is_allowed(rel):
                        build_from_relation(osm_data, rel)
                        rel.tags.pop(tag_value[0])
                        if "type" in rel.tags:
                            if rel.tags["type"] == "multipolygon":
                                rel.tags.pop("type")
                        found = True
                        break

        if found is False:
            for tag in build_tag:
                if tag in rel.tags:
                    if is_allowed(rel):
                        build_from_relation(osm_data, rel)
                        rel.tags.pop(tag)
                        if "type" in rel.tags:
                            if rel.tags["type"] == "multipolygon":
                                rel.tags.pop("type")
                        break


def build_from_relation(osm_data, rel):
    height, min_height = calculate_height(rel)

    for member in rel.members:
        way = osm.get_way_by_id(osm_data, member.ref)
        if way is not None:
            if member.role == "outer":
                build_from_way(way, height, min_height, from_relation=True)
            # FIXME: How to manager inner ?
            # elif member.role == "inner":


def build_from_way(way, height=None, min_height=None, from_relation=False):
    is_barrier = False
    if len(way.nodes) < 3:
        is_barrier = True

    calc_height, calc_min_height = calculate_height(way)

    if calc_height is not None:
        height = calc_height

    if calc_min_height is not None:
        min_height = calc_min_height

    if from_relation is True:
        object_3d.create_all_object_file(way.nodes, height, z=min_height, wall_texture=config.data["wall_texture"],
                                         roof_texture=config.data["roof_texture"], is_barrier=is_barrier)
    else:
        found = False
        for tag_value in build_tag_value:
            if tag_value[0] in way.tags:
                if way.tags[tag_value[0]] == tag_value[1]:
                    if is_allowed(way):
                        object_3d.create_all_object_file(way.nodes, height, z=min_height,
                                                         wall_texture=config.data["wall_texture"],
                                                         roof_texture=config.data["roof_texture"],
                                                         is_barrier=is_barrier)

                        way.tags.pop(tag_value[0])
                        found = True
                        break

        if found is False:
            for tag in build_tag:
                if tag in way.tags:
                    if is_allowed(way):
                        object_3d.create_all_object_file(way.nodes, height, z=min_height,
                                                         wall_texture=config.data["wall_texture"],
                                                         roof_texture=config.data["roof_texture"],
                                                         is_barrier=is_barrier)
                        way.tags.pop(tag)
                        break


def calculate_height(entity):
    height = None
    if "height" in entity.tags:
        height = float(entity.tags["height"])
        entity.tags.pop("height")

    if "building:levels" in entity.tags:
        level_qty = entity.tags["building:levels"]
        height = float(level_qty) * config.data["building_level_height"]
        entity.tags.pop("building:levels")

    min_height = None
    if "min_height" in entity.tags:
        min_height = float(entity.tags["min_height"])
        height = height - min_height
        entity.tags.pop("min_height")

    return height, min_height


def is_allowed(entity):
    for tag_value in negative_tag_value:
        if tag_value[0] in entity.tags:
            if entity.tags[tag_value[0]] == tag_value[1]:
                return False

    return True
