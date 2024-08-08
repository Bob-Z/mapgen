import config
import ogre_map_surface
import ogre_map_height
import object_3d


def process(entity, osm_data=None):
    if "amenity" in entity.tags:
        if entity.tags["amenity"] == "fountain":
            ogre_map_height.draw_entity(osm_data, entity,
                                        config.data["ground_line"] - config.data["fountain_depth"],
                                        config.data["ground_line"])
            entity.tags.pop("amenity")
            return True

    if "leisure" in entity.tags:
        if entity.tags["leisure"] == "swimming_pool":
            ogre_map_height.draw_entity_unblurred(osm_data, entity,
                                                  0.0, config.data["ground_line"])

            # FIXME only for ways, not for relations for now
            if hasattr(entity, "members") is False:
                # pool border
                object_3d.create_all_object_file(entity.nodes,
                                                 height=config.data["ground_line"] + config.data[
                                                     "swimming_pool_height"],
                                                 z=-config.data["ground_line"],
                                                 wall_texture="mapgen_dark_grey", top_texture="mapgen_dark_grey",
                                                 is_barrier=True, half_barrier=True, barrier_width=2.25)
                # pool bottom
                object_3d.create_all_object_file(entity.nodes,
                                                 height=config.data["ground_line"] - config.data["swimming_pool_depth"],
                                                 z=-config.data["ground_line"],
                                                 wall_texture="mapgen_dark_grey", top_texture="mapgen_dark_grey")

                entity.tags.pop("leisure")
            return True

    if "natural" in entity.tags:
        if entity.tags["natural"] == "water":
            ogre_map_height.draw_entity(osm_data, entity, config.data["water_depth"], config.data["ground_line"], force=True)
            ogre_map_surface.draw_rock_entity(osm_data, entity)
            entity.tags.pop("natural")

            if "type" in entity.tags:
                if entity.tags["type"] == "multipolygon":
                    entity.tags.pop("type")

            return True

    return False
