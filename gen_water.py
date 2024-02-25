import config
import ogre_map_surface
import ogre_map_height


def process(entity, osm_data=None):
    if "amenity" in entity.tags:
        if entity.tags["amenity"] == "fountain":
            ogre_map_height.draw_entity(osm_data, entity,
                                        config.data["ground_line"] - config.data["fountain_depth"], config.data["ground_line"])
            entity.tags.pop("amenity")
            return True

    if "leisure" in entity.tags:
        if entity.tags["leisure"] == "swimming_pool":
            ogre_map_height.draw_entity(osm_data, entity,
                                        config.data["ground_line"] - config.data["swimming_pool_depth"], config.data["ground_line"])
            entity.tags.pop("leisure")
            return True

    if "natural" in entity.tags:
        if entity.tags["natural"] == "water":
            ogre_map_height.draw_entity(osm_data, entity, config.data["water_depth"], config.data["ground_line"])
            ogre_map_surface.draw_rock_entity(osm_data, entity)
            entity.tags.pop("natural")
            return True

    return False
