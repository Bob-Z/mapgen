import object_3d
import config
import osm
import topography

shelter_tag_value = [["amenity", "shelter"], ["building", "roof"], ["shelter", "yes"]]
shelter_tag = []


def process(entity, osm_data=None):
    for tag_value in shelter_tag_value:
        if tag_value[0] in entity.tags:
            if entity.tags[tag_value[0]] == tag_value[1]:
                if osm_data is None:
                    build_from_way(entity)
                else:
                    build_from_relation(osm_data, entity)
                entity.tags.pop(tag_value[0])
                if "type" in entity.tags:
                    if entity.tags["type"] == "multipolygon":
                        entity.tags.pop("type")
                return True

    for tag in shelter_tag:
        if tag in entity.tags:
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
    height, min_height, roof_height = osm.get_height(rel)

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

    calc_height, calc_min_height, calc_roof_height = osm.get_height(way)

    if calc_height is not None:
        height = calc_height

    if calc_min_height is not None:
        min_height = calc_min_height

    if calc_roof_height is not None:
        roof_height = calc_roof_height

    build_shelter(way, height, min_height, is_barrier)


def build_shelter(way, height, min_height, is_barrier):
    if height is None:
        height = config.data["building_level_height"] - config.data["shelter_ceiling"]
    else:
        height = height - config.data["shelter_ceiling"]

    if min_height is None:
        min_height = 0.0

    # Pillars
    for node in way.nodes:
        group_z = 0.0
        z = topography.get_z(node.lon, node.lat)
        if z > group_z:
            group_z = z

    for node in way.nodes:
        object_3d.create_all_object_file([node], height, z=min_height,
                                         wall_texture=config.data["wall_texture"],
                                         top_texture=config.data["top_texture"],
                                         is_barrier=is_barrier,
                                         group_z=group_z)
    # Roof
    # Z is pillars' height
    object_3d.create_all_object_file(way.nodes, config.data["shelter_ceiling"], z=height + min_height,
                                     wall_texture=config.data["wall_texture"],
                                     top_texture=config.data["top_texture"], is_barrier=is_barrier)

    # floor
    object_3d.create_all_object_file(way.nodes, config.data["shelter_floor"], z=min_height,
                                     wall_texture=config.data["wall_texture"],
                                     top_texture=config.data["top_texture"], is_barrier=is_barrier)
