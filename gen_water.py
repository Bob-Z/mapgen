import object_3d
import config
import ogre_material


def process(osm_data):
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

        #if "waterway" in way.tags:
        #    object_3d.create_all_object_file(way.nodes, elevation=config.data["water_height"],
        #                                     wall_texture="mapgen_blue",
        #                                     roof_texture="mapgen_blue")
        #   way.tags.pop("waterway")
