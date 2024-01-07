import gen_land
import config
import ogre_material


def process(entity, osm_data=None):
    if "amenity" in entity.tags:
        if entity.tags["amenity"] == "fountain":
            gen_land.create_from_entity(osm_data, entity, height=config.data["water_height"], z=0.0,
                                        wall_texture="mapgen_blue", roof_texture="mapgen_blue")

            entity.tags.pop("amenity")
            return True

    if "leisure" in entity.tags:
        if entity.tags["leisure"] == "swimming_pool":
            gen_land.create_from_entity(osm_data, entity, height=config.data["swimming_pool_height"], z=0.0,
                                        wall_texture="mapgen_swimming_pool", roof_texture=None,
                                        roof_texture_generator=ogre_material.create_material_swimming_pool)
            entity.tags.pop("leisure")
            return True

    if "natural" in entity.tags:
        if entity.tags["natural"] == "water":
            gen_land.create_from_entity(osm_data, entity, height=config.data["water_height"], z=0.0,
                                        wall_texture="mapgen_blue", roof_texture="mapgen_blue")
            entity.tags.pop("natural")
            return True

    return False
