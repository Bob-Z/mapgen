import object_3d
import config
import osm


def process(osm_data):
    print("Generating buildings")
    for way in osm_data.ways:
        build_from_way(way)

    for rel in osm_data.relations:
        if "building" in rel.tags:
            if rel.tags["building"] == "yes":
                for member in rel.members:
                    way = osm.get_way_by_id(osm_data, member.ref)
                    if way is not None:
                        if member.role == "outer":
                            build_from_way(way, from_relation=True)
                        # FIXME: How to manager inner ?
#                        elif member.role == "inner":
#                            object_3d.create_all_object_file(way.nodes, height=config.data["island_height"],
#                                                             wall_texture="mapgen_beige",
#                                                             roof_texture="mapgen_beige")

                rel.tags.pop("building")


def build_from_way(way, from_relation=False):
    level_qty = 1
    if "building:levels" in way.tags:
        level_qty = way.tags["building:levels"]
        way.tags.pop("building:levels")
    height = float(level_qty) * config.data["building_level_height"]

    if from_relation is True:
        object_3d.create_all_object_file(way.nodes, height, wall_texture=config.data["wall_texture"],
                                         roof_texture=config.data["roof_texture"])
    else:
        if "amenity" in way.tags:
            if way.tags["amenity"] == "shelter":
                object_3d.create_all_object_file(way.nodes, height, wall_texture="mapgen_red",
                                                 roof_texture="mapgen_red")

                way.tags.pop("amenity")

        elif "building" in way.tags:
            object_3d.create_all_object_file(way.nodes, height=height, wall_texture=config.data["wall_texture"],
                                             roof_texture=config.data["roof_texture"],
                                             is_barrier=False, roof_texture_generator=None)
            way.tags.pop("building")
        elif "disused:building" in way.tags:
            object_3d.create_all_object_file(way.nodes, height=height, wall_texture=config.data["wall_texture"],
                                             roof_texture=config.data["roof_texture"],
                                             is_barrier=False, roof_texture_generator=None)
            way.tags.pop("disused:building")
        elif "demolished:building" in way.tags:
            object_3d.create_all_object_file(way.nodes, height=height, wall_texture=config.data["wall_texture"],
                                             roof_texture=config.data["roof_texture"],
                                             is_barrier=False, roof_texture_generator=None)
            way.tags.pop("demolished:building")
