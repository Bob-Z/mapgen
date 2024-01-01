import object_3d
import config
import ogre_material
import osm


def process(osm_data):
    print("Generating water")
    for way in osm_data.ways:
        if "amenity" in way.tags:
            if way.tags["amenity"] == "fountain":
                object_3d.create_all_object_file(way.nodes, height=config.data["water_height"],
                                                 wall_texture="mapgen_blue", roof_texture="mapgen_blue")

                way.tags.pop("amenity")

        elif "leisure" in way.tags:
            if way.tags["leisure"] == "swimming_pool":
                object_3d.create_all_object_file(way.nodes, height=config.data["swimming_pool_height"],
                                                 wall_texture="mapgen_swimming_pool",
                                                 roof_texture_generator=ogre_material.create_material_swimming_pool)

                way.tags.pop("leisure")

        elif "natural" in way.tags:
            if way.tags["natural"] == "water":
                object_3d.create_all_object_file(way.nodes, height=config.data["water_height"],
                                                 wall_texture="mapgen_blue",
                                                 roof_texture="mapgen_blue")
                way.tags.pop("natural")

        # if "waterway" in way.tags:
        #    object_3d.create_all_object_file(way.nodes, elevation=config.data["water_height"],
        #                                     wall_texture="mapgen_blue",
        #                                     roof_texture="mapgen_blue")
        #   way.tags.pop("waterway")

    for rel in osm_data.relations:
        if "natural" in rel.tags:
            if rel.tags["natural"] == "water":
                for member in rel.members:
                    way = osm.get_way_by_id(osm_data, member.ref)
                    if way is not None:
                        if member.role == "outer":
                            object_3d.create_all_object_file(way.nodes, height=config.data["water_height"],
                                                             wall_texture="mapgen_blue",
                                                             roof_texture="mapgen_blue")
                        elif member.role == "inner":
                            object_3d.create_all_object_file(way.nodes, height=config.data["island_height"],
                                                             wall_texture="mapgen_beige",
                                                             roof_texture="mapgen_beige")

                rel.tags.pop("natural")
