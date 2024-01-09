import object_3d
import config
import osm

build_tag_value = [["type", "building"], ['man_made', 'street_cabinet']]
build_tag = ["building:part", "building"]
negative_tag_value = [["amenity", "shelter"]]
if config.data["hide_wiki"] is True:
    negative_tag = ["wikipedia", "wikidata"]
else:
    negative_tag = []


def process(entity, osm_data=None):
    for tag_value in build_tag_value:
        if tag_value[0] in entity.tags:
            if entity.tags[tag_value[0]] == tag_value[1]:
                if is_allowed(entity):
                    if osm_data is None:
                        build_from_way(entity)
                    else:
                        build_from_relation(osm_data, entity)
                    entity.tags.pop(tag_value[0])
                    if "type" in entity.tags:
                        if entity.tags["type"] == "multipolygon":
                            entity.tags.pop("type")
                    return True

    for tag in build_tag:
        if tag in entity.tags:
            if is_allowed(entity):
                if osm_data is None:
                    build_from_way(entity)
                else:
                    build_from_relation(osm_data, entity)
                entity.tags.pop(tag)
                if "type" in entity.tags:
                    if entity.tags["type"] == "multipolygon":
                        entity.tags.pop("type")
                return True

    return False


def build_from_relation(osm_data, rel):
    height, min_height = get_height(rel)

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

    calc_height, calc_min_height = get_height(way)

    if calc_height is not None:
        height = calc_height

    if calc_min_height is not None:
        min_height = calc_min_height

    object_3d.create_all_object_file(way.nodes, height, z=min_height,
                                     wall_texture=config.data["wall_texture"],
                                     roof_texture=config.data["roof_texture"],
                                     is_barrier=is_barrier)


def get_height(entity):
    height = None

    if "building:levels" in entity.tags:
        level_qty = entity.tags["building:levels"]
        try:
            height = float(level_qty) * config.data["building_level_height"]
            entity.tags.pop("building:levels")
        except ValueError:
            print("Cannot convert building:levels : " + entity.tags["building:levels"])

    if "height" in entity.tags:
        h = entity.tags["height"]

        convert_rate = 1.0
        h = h.replace(' m', '')  # Some height appear like: 100 m
        if h.find(" ft") != -1:
            h = h.replace(' ft', '')
            convert_rate = 0.3048
        if h.find(" storey") != -1:
            h = h.replace(' storey', '')
            convert_rate = config.data["building_level_height"]

        try:
            height = float(h) * convert_rate
            entity.tags.pop("height")
        except ValueError:
            print("Cannot convert height: " + entity.tags["height"])

    min_height = None
    if "min_height" in entity.tags:
        if height is None:
            height = config.data["building_level_height"]
        try:
            min_height = float(entity.tags["min_height"])
            height = height - min_height
            entity.tags.pop("min_height")
        except ValueError:
            print("Cannot convert min_height: " + entity.tags["min_height"])

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
