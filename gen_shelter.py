import object_3d
import config
import osm
import gen_building

build_tag_value = [["amenity", "shelter"]]
build_tag = []


def process(osm_data):
    print("Generating shelters")
    for way in osm_data.ways:
        build_from_way(way)

    for rel in osm_data.relations:
        found = False
        for tag_value in build_tag_value:
            if tag_value[0] in rel.tags:
                if rel.tags[tag_value[0]] == tag_value[1]:
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
                    build_from_relation(osm_data, rel)
                    rel.tags.pop(tag)
                    if "type" in rel.tags:
                        if rel.tags["type"] == "multipolygon":
                            rel.tags.pop("type")
                    break


def build_from_relation(osm_data, rel):
    height, min_height = gen_building.calculate_height(rel)

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

    calc_height, calc_min_height = gen_building.calculate_height(way)

    if calc_height is not None:
        height = calc_height

    if calc_min_height is not None:
        min_height = calc_min_height

    if from_relation is True:
        build_shelter(way, height, min_height, is_barrier)
    else:
        found = False
        for tag_value in build_tag_value:
            if tag_value[0] in way.tags:
                if way.tags[tag_value[0]] == tag_value[1]:
                    build_shelter(way, height, min_height, is_barrier)
                    way.tags.pop(tag_value[0])
                    found = True
                    break

        if found is False:
            for tag in build_tag:
                if tag in way.tags:
                    build_shelter(way, height, min_height, is_barrier)
                    way.tags.pop(tag)
                    break


def build_shelter(way, height, min_height, is_barrier):
    if height is None:
        height = config.data["building_level_height"] - config.data["shelter_roof_height"]
    else:
        height = height - config.data["shelter_roof_height"]

    if min_height is None:
        min_height = 0.0

        # Pillars
    for node in way.nodes:
        object_3d.create_all_object_file([node], height, z=min_height,
                                         wall_texture=config.data["wall_texture"],
                                         roof_texture=config.data["roof_texture"],
                                         is_barrier=is_barrier)
        # Roof
        # Z is pillars' height
    object_3d.create_all_object_file(way.nodes, config.data["shelter_roof_height"], z=height + min_height,
                                     wall_texture=config.data["wall_texture"],
                                     roof_texture=config.data["roof_texture"], is_barrier=is_barrier)
