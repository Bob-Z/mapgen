import ogre_material
import object_3d
import config
import osm
from wikidata.client import Client
from pyWikiCommons import pyWikiCommons

wikidata_client = Client()

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
    ["shelter_type", "public_transport"],
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
    height, min_height, roof_height = osm.get_height(rel)

    # if build_from_wikidata(rel, osm_data) is True:
    #    return

    for member in rel.members:
        way = osm.get_way_by_id(osm_data, member.ref)
        if way is not None:
            if member.role == "outer" or member.role == "part":  # Don't draw outline, it breaks Paris Eiffel Tower
                build_from_way(way, height, min_height, roof_height)
            # FIXME: How to manager inner ?
            # elif member.role == "inner":

            way.tags["mapgen"] = "used_by_relation"


def build_from_way(way, height=None, min_height=None, roof_height=None):
    if "mapgen" in way.tags and way.tags["mapgen"] == "used_by_relation":
        return

    # if build_from_wikidata(way) is True:
    #    return

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

    wall_texture = None
    top_texture = None

    if "colour" in way.tags:
        wall_texture = ogre_material.create_material_color(way.tags["colour"])
        way.tags.pop("colour")
    if "building:colour" in way.tags:
        wall_texture = ogre_material.create_material_color(way.tags["building:colour"])
        way.tags.pop("building:colour")
    if "roof:colour" in way.tags:
        top_texture = ogre_material.create_material_color(way.tags["roof:colour"])
        way.tags.pop("roof:colour")
    display_name = None
    if "name:en" in way.tags:
        display_name = way.tags["name:en"]
    else:
        if "name" in way.tags:
            display_name = way.tags["name"]

    if wall_texture is None:
        wall_texture = config.data["wall_texture"]
    if top_texture is None:
        top_texture = config.data["top_texture"]

    roof_shape = None
    if "roof:shape" in way.tags:
        roof_shape = way.tags["roof:shape"]
        way.tags.pop("roof:shape")

        if top_texture is None and object_3d.is_roof_shape_supported(roof_shape) and roof_height is not None and roof_shape != "flat":
            top_texture = config.data["roof_texture"]

    object_3d.create_all_object_file(way.nodes, height, z=min_height,
                                     wall_texture=wall_texture,
                                     top_texture=top_texture,
                                     is_barrier=is_barrier,
                                     roof_shape=roof_shape,
                                     roof_height=roof_height,
                                     display_name=display_name)


# Return True if the building has been build
def build_from_wikidata(entity, osm_data=None):
    found = False

    if "wikidata" in entity.tags:
        wiki = wikidata_client.get(entity.tags["wikidata"], load=True)
        if "P4896" in wiki.attributes["claims"]:
            name = wiki.attributes["claims"]["P4896"][0]["mainsnak"]["datavalue"]["value"]
            # pyWikiCommons.download_commons_image(name, config.data["work_path"])
            print("P4896 available for entity", entity, name)
            found = True

    if found is False and osm_data is not None:
        for member in entity.members:
            way = osm.get_way_by_id(osm_data, member.ref)
            if way is not None:
                if build_from_wikidata(way) is True:
                    found = True
                    break

    # Remove all ways of the relation
    if found is True and osm_data is not None:
        for member in entity.members:
            index = 0
            while index < len(osm_data.ways):
                if osm_data.ways[index].id == member.ref:
                    osm_data.way_ids.pop(index)
                    osm_data.ways.pop(index)
                    print("remove", osm_data.ways[index])
                    break
                index += 1

    return found


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
