import object_3d
import config
import osm

build_tag_value = [["type", "building"], ['man_made', 'street_cabinet'], ['man_made', 'reservoir_covered'],
                   ['man_made', 'pumping_station']]
build_tag = ["building:part", "building"]
negative_tag_value = [["amenity", "shelter"], ["building", "roof"]]
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

    h = None
    if "height" in entity.tags:
        h = convert_height_to_meter(entity.tags["height"])
        if h is not None:
            height = h
            entity.tags.pop("height")

    if h is None and "est_roof:height" in entity.tags:
        h = convert_height_to_meter(entity.tags["est_roof:height"])
        if h is not None:
            height = h
            entity.tags.pop("est_roof:height")

    min_height = None
    if "min_height" in entity.tags:
        height, min_height = get_min_height(height, convert_height_to_meter(entity.tags["min_height"]))
        if min_height is not None:
            entity.tags.pop("min_height")
    elif "building:min_level" in entity.tags:
        level_qty = entity.tags["building:min_level"]
        min_h = None
        try:
            min_h = float(level_qty) * config.data["building_level_height"]
        except ValueError:
            print("Cannot convert building:levels : " + entity.tags["building:min_level"])

        height, min_height = get_min_height(height, min_h)
        if min_height is not None:
            entity.tags.pop("building:min_level")

    return height, min_height


def get_min_height(height, min_height):
    if min_height is not None:
        if height is None:
            height = config.data["building_level_height"]
        else:
            height = height - min_height

    return height, min_height


def convert_height_to_meter(height):
    height_in_meter = None

    convert_rate = 1.0
    height = height.replace(' m', '')  # Some height appear like: 100 m
    if height.find(" ft") != -1:
        height = height.replace(' ft', '')
        convert_rate = 0.3048
    if height.find(" storey") != -1:
        height = height.replace(' storey', '')
        convert_rate = config.data["building_level_height"]

    try:
        height_in_meter = float(height) * convert_rate
    except ValueError:
        print("Cannot convert height: " + height)

    return height_in_meter


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
