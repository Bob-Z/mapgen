import config
import ogre_map_surface
import ogre_map_height
import object_3d
import ror_tobj_file
import osm


def process(feature):
    if "amenity" in feature["properties"]["tags"]:
        if feature["properties"]["tags"]["amenity"] == "fountain":
            ogre_map_height.draw_feature(feature,
                                        config.data["ground_line"] - config.data["fountain_depth"],
                                        config.data["ground_line"])
            feature["properties"]["tags"].pop("amenity")
            return True

    if "leisure" in feature["properties"]["tags"]:
        if feature["properties"]["tags"]["leisure"] == "swimming_pool":
            ogre_map_height.draw_feature_unblurred(feature,
                                                   0.0, config.data["ground_line"])

            object_3d.create_all_object_file(osm.get_coord_from_feature(feature),
                                             height=config.data["ground_line"] + config.data[
                                                 "swimming_pool_height"],
                                             z=-config.data["ground_line"],
                                             wall_texture="mapgen_dark_grey", top_texture="mapgen_dark_grey",
                                             is_barrier=True, half_barrier=True, barrier_width=2.25)
            # pool bottom
            object_3d.create_all_object_file(osm.get_coord_from_feature(feature),
                                             height=config.data["ground_line"] - config.data["swimming_pool_depth"],
                                             z=-config.data["ground_line"],
                                             wall_texture="mapgen_dark_grey", top_texture="mapgen_dark_grey")

            feature["properties"]["tags"].pop("leisure")

            return True

    if "natural" in feature["properties"]["tags"]:
        if feature["properties"]["tags"]["natural"] == "water":
            ogre_map_height.draw_feature(feature, config.data["water_depth"], config.data["ground_line"], force=True)
            ogre_map_surface.draw_rock_feature(feature)
            ror_tobj_file.add_grass(feature, "seaweed")
            feature["properties"]["tags"].pop("natural")

            return True

    return False
