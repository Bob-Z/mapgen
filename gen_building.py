import object_3d
import config
import osm


def process(osm_data):
    print("Generating buildings")
    for way in osm_data.ways:
        build_from_way(way)

    for rel in osm_data.relations:
        if "building" in rel.tags:
            if rel.tags["building"] == "yes" or rel.tags["building"] == "industrial":
                build_from_relation(osm_data, rel)
                rel.tags.pop("building")

        elif "building:part" in rel.tags:
            if rel.tags["building:part"] == "yes":
                build_from_relation(osm_data, rel)
                rel.tags.pop("building:part")


def build_from_relation(osm_data, rel):
    height = None
    if "height" in rel.tags:
        height = float(rel.tags["height"])
        rel.tags.pop("height")

    min_height = 0.0
    if "min_height" in rel.tags:
        min_height = float(rel.tags["min_height"])
        height = height - min_height
        rel.tags.pop("min_height")

    for member in rel.members:
        way = osm.get_way_by_id(osm_data, member.ref)
        if way is not None:
            if member.role == "outer":
                build_from_way(way, height, min_height, from_relation=True)
            # FIXME: How to manager inner ?
            # elif member.role == "inner":


def build_from_way(way, height=None, min_height=0.0, from_relation=False):
    is_barrier = False
    if len(way.nodes) < 3:
        is_barrier = True

    if height is None:
        height = config.data["building_level_height"]

    if "building:levels" in way.tags:
        level_qty = way.tags["building:levels"]
        way.tags.pop("building:levels")
        height = float(level_qty) * config.data["building_level_height"]

    if "height" in way.tags:
        height = float(way.tags["height"])
        way.tags.pop("height")

    if from_relation is True:
        object_3d.create_all_object_file(way.nodes, height, z=min_height, wall_texture=config.data["wall_texture"],
                                         roof_texture=config.data["roof_texture"], is_barrier=is_barrier)
    else:
        if "amenity" in way.tags:
            if way.tags["amenity"] == "shelter":
                object_3d.create_all_object_file(way.nodes, height=height, wall_texture="mapgen_red",
                                                 roof_texture="mapgen_red", is_barrier=is_barrier)

                way.tags.pop("amenity")

        elif "building" in way.tags:
            object_3d.create_all_object_file(way.nodes, height=height, wall_texture=config.data["wall_texture"],
                                             roof_texture=config.data["roof_texture"],
                                             is_barrier=is_barrier, roof_texture_generator=None)
            way.tags.pop("building")
        elif "disused:building" in way.tags:
            object_3d.create_all_object_file(way.nodes, height=height, wall_texture=config.data["wall_texture"],
                                             roof_texture=config.data["roof_texture"],
                                             is_barrier=is_barrier, roof_texture_generator=None)
            way.tags.pop("disused:building")
        elif "demolished:building" in way.tags:
            object_3d.create_all_object_file(way.nodes, height=height, wall_texture=config.data["wall_texture"],
                                             roof_texture=config.data["roof_texture"],
                                             is_barrier=is_barrier, roof_texture_generator=None)
            way.tags.pop("demolished:building")
