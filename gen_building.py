import object_3d
import config
import ogre_material
import osm

build_tag_value = [
    # first pass
    [
        ["building:part", "yes"],
    ],
    # second pass
    [
        ["building", None],
        ["type", "building"],
        ['man_made', 'street_cabinet'],
        ['man_made', 'reservoir_covered'],
        ['man_made', 'pumping_station'],
        ['man_made', 'wastewater_plant']
    ]
]

negative_tag_value = [
    ["amenity", "shelter"],
    ["building", "roof"],
    ["landuse", None],
]


def process(entity, osm_data=None, pass_index=0):
    for tag_value in build_tag_value[pass_index]:
        if tag_value[0] in entity.tags:
            if tag_value[1] is not None:
                if entity.tags[tag_value[0]] != tag_value[1]:
                    continue
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

    return False


def build_from_relation(osm_data, rel):
    height, min_height = osm.get_height(rel)

    for member in rel.members:
        way = osm.get_way_by_id(osm_data, member.ref)
        if way is not None:
            if member.role == "outer" or member.role == "outline" or member.role == "part":
                build_from_way(way, height, min_height)
            # FIXME: How to manager inner ?
            # elif member.role == "inner":

            way.tags["mapgen"] = "used_by_relation"


def build_from_way(way, height=None, min_height=None):
    if "mapgen" in way.tags and way.tags["mapgen"] == "used_by_relation":
        return

    is_barrier = False
    if len(way.nodes) < 3:
        is_barrier = True

    calc_height, calc_min_height = osm.get_height(way)

    if calc_height is not None:
        height = calc_height

    if calc_min_height is not None:
        min_height = calc_min_height

    wall_texture = None
    roof_texture = None

    if "colour" in way.tags:
        wall_texture = ogre_material.create_material_color(way.tags["colour"])
        way.tags.pop("colour")
    if "building:colour" in way.tags:
        wall_texture = ogre_material.create_material_color(way.tags["building:colour"])
        way.tags.pop("building:colour")
    if "roof:colour" in way.tags:
        roof_texture = ogre_material.create_material_color(way.tags["roof:colour"])
        way.tags.pop("roof:colour")

    if wall_texture is None:
        wall_texture = config.data["wall_texture"]
    if roof_texture is None:
        roof_texture = config.data["roof_texture"]

    object_3d.create_all_object_file(way.nodes, height, z=min_height,
                                     wall_texture=wall_texture,
                                     roof_texture=roof_texture,
                                     is_barrier=is_barrier)


def is_allowed(entity):
    for tag_value in negative_tag_value:
        if tag_value[0] in entity.tags:
            if tag_value[1] is not None:
                if entity.tags[tag_value[0]] == tag_value[1]:
                    return False
            else:
                return None

    if "level" in entity.tags:
        if entity.tags["level"][0] == '-':  # Skip negative levels
            return False

    return True
