import object_3d
import config
import osm

build_tag_value = [["type", "building"], ['man_made', 'street_cabinet']]
build_tag = ["building:part", "building"]
negative_tag_value = [["amenity", "shelter"]]
negative_tag = ["wikipedia", "wikidata"]

def process(osm_data):
    print("Generating buildings")

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

    for way in osm_data.ways:
        build_from_way(way)


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
        way.tags["mapgen"] = "done"  # Avoid ways being processed 2 times
    else:
        if "mapgen" in way.tags:
            way.tags.pop("mapgen")
            return
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

    if "building:levels" in entity.tags:
        level_qty = entity.tags["building:levels"]
        height = float(level_qty) * config.data["building_level_height"]
        entity.tags.pop("building:levels")

    if "height" in entity.tags:
        convert_rate = 1.0
        h = entity.tags["height"]
        h = h.replace(' m', '')  # Some height appear like: 100 m
        if h.find(" ft") != -1:
            h = h.replace(' ft', '')
            convert_rate = 0.3048
        if h.find(" storey") != -1:
            h = h.replace(' storey', '')
            convert_rate = config.data["building_level_height"]
        height = float(h) * convert_rate
        entity.tags.pop("height")

    min_height = None
    if "min_height" in entity.tags:
        if height is None:
            height = config.data["building_level_height"]
        min_height = float(entity.tags["min_height"])
        height = height - min_height
        entity.tags.pop("min_height")

    return height, min_height


def is_allowed(entity):
    for tag_value in negative_tag_value:
        if tag_value[0] in entity.tags:
            if entity.tags[tag_value[0]] == tag_value[1]:
                return False

    for tag in negative_tag:
        if tag in entity.tags:
            return False

    if "level" in entity.tags:
        if entity.tags["level"][0] == '-':  # Skip negative levels
            return False

    return True
