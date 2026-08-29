import ogre_material
import object_3d
import config
import osm
import wiki

build_tag_value = [
    # first pass
    [
        ["building:part", None],
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
    ["shelter_type", "public_transport"],
]

building_created_qty = 0
building_discovered_qty = 0


# Return True if feature as been processed successfully
def process(feature, osm_data=None, pass_index=0):
    for tag_value in build_tag_value[pass_index]:
        if tag_value[0] in feature["properties"]["tags"]:
            if tag_value[1] is not None:
                if feature["properties"]["tags"][tag_value[0]] != tag_value[1]:
                    continue
            if is_allowed(feature):
                if osm_data is None:
                    build_from_way(feature)
                else:
                    build_from_relation(osm_data, feature)
                feature["properties"]["tags"].pop(tag_value[0])
                if "type" in feature["properties"]["tags"]:
                    if feature["properties"]["tags"]["type"] == "multipolygon":
                        feature["properties"]["tags"].pop("type")
                return True

    return False


def build_from_relation(osm_data, rel):
    height, min_height, roof_height = osm.get_height(rel)

    for member in rel.members:
        way = osm.get_way_by_id(osm_data, member.ref)
        if way is not None:
            if member.role == "outer" or member.role == "part":  # Don't draw outline, it breaks Paris Eiffel Tower
                if build_from_way(way, height, min_height, roof_height) is True:
                    feature["properties"]["tags"]["mapgen"] = "used_by_relation"
            # FIXME: How to manager inner ?
            # elif member.role == "inner":
            else:
                feature["properties"]["tags"]["mapgen"] = "skip_outer"


# Return True if a building has been created
def build_from_way(feature, height=None, min_height=None, roof_height=None):
    if "mapgen" in feature["properties"]["tags"] and feature["properties"]["tags"]["mapgen"] == "used_by_relation":
        return False

    if wiki.is_object_crossing(feature["geometry"]["coordinates"][0]) is True:
        return False

    is_barrier = False
    if len(feature["geometry"]["coordinates"][0]) < 3:
        is_barrier = True

    calc_height, calc_min_height, calc_roof_height = osm.get_height(feature)

    if calc_height is not None:
        height = calc_height

    if calc_min_height is not None:
        min_height = calc_min_height

    if calc_roof_height is not None:
        roof_height = calc_roof_height

    wall_texture = None
    top_texture = None

    wall_texture = ogre_material.create_material_color(feature["properties"]["tags"])

    display_name = None
    if "name:en" in feature["properties"]["tags"]:
        display_name = feature["properties"]["tags"]["name:en"]
    else:
        if "name" in feature["properties"]["tags"]:
            display_name = feature["properties"]["tags"]["name"]

    roof_shape = None
    if "roof:shape" in feature["properties"]["tags"]:
        roof_shape = feature["properties"]["tags"]["roof:shape"]
        feature["properties"]["tags"].pop("roof:shape")

        if top_texture is None and object_3d.is_roof_shape_supported(
                roof_shape) and roof_height is not None and roof_shape != "flat":
            top_texture = config.data["roof_texture"]

    if wall_texture is None:
        wall_texture = config.data["wall_texture"]
    if top_texture is None:
        top_texture = config.data["top_texture"]

    global building_discovered_qty
    global building_created_qty

    building_discovered_qty += 1

    if building_created_qty / building_discovered_qty < config.data["building_ratio"]:
        building_created_qty += 1

        object_3d.create_all_object_file(feature["geometry"]["coordinates"][0], height, z=min_height,
                                         wall_texture=wall_texture,
                                         top_texture=top_texture,
                                         is_barrier=is_barrier,
                                         roof_shape=roof_shape,
                                         roof_height=roof_height,
                                         display_name=display_name)

        return True
    else:
        return False


def is_allowed(feature):
    for tag_value in negative_tag_value:
        if tag_value[0] in feature["properties"]["tags"]:
            if tag_value[1] is not None:
                if feature["properties"]["tags"][tag_value[0]] == tag_value[1]:
                    return False
            else:
                return None

    if "level" in feature["properties"]["tags"]:
        if feature["properties"]["tags"]["level"][0] == '-':  # Skip negative levels
            return False

    return True
