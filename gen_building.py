import object_3d
import config
import osm

build_tag_value = [
    ["type", "building"],
    ['man_made', 'street_cabinet'],
    ['man_made', 'reservoir_covered'],
    ['man_made', 'pumping_station'],
    ['man_made', 'wastewater_plant']
]

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
    height, min_height = osm.get_height(rel)

    for member in rel.members:
        way = osm.get_way_by_id(osm_data, member.ref)
        if way is not None:
            if member.role == "outer":
                build_from_way(way, height, min_height)
            # FIXME: How to manager inner ?
            # elif member.role == "inner":


def build_from_way(way, height=None, min_height=None):
    is_barrier = False
    if len(way.nodes) < 3:
        is_barrier = True

    calc_height, calc_min_height = osm.get_height(way)

    if calc_height is not None:
        height = calc_height

    if calc_min_height is not None:
        min_height = calc_min_height

    object_3d.create_all_object_file(way.nodes, height, z=min_height,
                                     wall_texture=config.data["wall_texture"],
                                     roof_texture=config.data["roof_texture"],
                                     is_barrier=is_barrier)


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
