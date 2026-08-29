import config
import ogre_map_surface
import ogre_map_height
import object_3d
import ror_tobj_file


def process(feature, osm_data=None):
    if "amenity" in feature["properties"]["tags"]:
        if feature["properties"]["tags"]["amenity"] == "fountain":
            ogre_map_height.draw_entity(osm_data, entity,
                                        config.data["ground_line"] - config.data["fountain_depth"],
                                        config.data["ground_line"])
            feature["properties"]["tags"].pop("amenity")
            return True

    if "leisure" in feature["properties"]["tags"]:
        if feature["properties"]["tags"]["leisure"] == "swimming_pool":
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

                feature["properties"]["tags"].pop("leisure")
            return True

    if "natural" in feature["properties"]["tags"]:
        if feature["properties"]["tags"]["natural"] == "water":
            ogre_map_height.draw_entity(osm_data, entity, config.data["water_depth"], config.data["ground_line"], force=True)
            ogre_map_surface.draw_rock_entity(osm_data, entity)
            ror_tobj_file.add_grass(osm_data, entity, "seaweed")
            feature["properties"]["tags"].pop("natural")

            if "type" in feature["properties"]["tags"]:
                if feature["properties"]["tags"]["type"] == "multipolygon":
                    feature["properties"]["tags"].pop("type")

            return True

    return False
