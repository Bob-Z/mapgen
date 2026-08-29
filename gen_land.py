import ogre_map_surface
import ror_tobj_file
import ogre_map_height
import config


def process(feature, osm_data=None):
    if "amenity" in feature["properties"]["tags"]:
        if feature["properties"]["tags"]["amenity"] == "parking":
            ogre_map_surface.draw_asphalt_feature(osm_data, feature)
            feature["properties"]["tags"].pop("amenity")
            return True
    if "leisure" in feature["properties"]["tags"]:
        if feature["properties"]["tags"]["leisure"] == "park":
            ogre_map_surface.draw_grass_feature(osm_data, feature)
            ror_tobj_file.add_grass(osm_data, feature, "grass2")
            feature["properties"]["tags"].pop("leisure")
            return True
        if feature["properties"]["tags"]["leisure"] == "pitch":
            if "surface" in feature["properties"]["tags"] and feature["properties"]["tags"]["surface"] == "asphalt":
                ogre_map_surface.draw_asphalt_feature(osm_data, feature)
                feature["properties"]["tags"].pop("surface")
            elif "surface" in feature["properties"]["tags"] and feature["properties"]["tags"]["surface"] == "clay":
                ogre_map_surface.draw_gravel_feature(osm_data, feature)
                feature["properties"]["tags"].pop("surface")
            else:
                ogre_map_surface.draw_grass_feature(osm_data, feature)
            feature["properties"]["tags"].pop("leisure")
            return True
        if feature["properties"]["tags"]["leisure"] == "playground":
            if "surface" in feature["properties"]["tags"] and feature["properties"]["tags"]["surface"] == "compacted":
                ogre_map_surface.draw_sand_feature(osm_data, feature)
                feature["properties"]["tags"].pop("surface")
            else:
                ogre_map_surface.draw_grass_feature(osm_data, feature)
            feature["properties"]["tags"].pop("leisure")
            return True
        if feature["properties"]["tags"]["leisure"] == "sports_centre":
            ogre_map_surface.draw_asphalt_feature(osm_data, feature)
            feature["properties"]["tags"].pop("leisure")
            return True
        if feature["properties"]["tags"]["leisure"] == "track":
            if "surface" in feature["properties"]["tags"] and feature["properties"]["tags"]["surface"] == "compacted":
                ogre_map_surface.draw_sand_feature(osm_data, feature)
                feature["properties"]["tags"].pop("surface")
            else:
                ogre_map_surface.draw_asphalt_feature(osm_data, feature)
            feature["properties"]["tags"].pop("leisure")
            return True

    if "landuse" in feature["properties"]["tags"]:
        if feature["properties"]["tags"]["landuse"] == "grass" or feature["properties"]["tags"]["landuse"] == "recreation_ground":
            ogre_map_surface.draw_grass_feature(osm_data, feature)
            ror_tobj_file.add_grass(osm_data, feature, "grass3")
            feature["properties"]["tags"].pop("landuse")
            return True
        if feature["properties"]["tags"]["landuse"] == "construction" or feature["properties"]["tags"]["landuse"] == "industrial" or feature["properties"]["tags"][
            "landuse"] == "residential" or feature["properties"]["tags"]["landuse"] == "retail" or feature["properties"]["tags"]["landuse"] == "education":
            ogre_map_surface.draw_asphalt_feature(osm_data, feature)
            feature["properties"]["tags"].pop("landuse")
            return True
        if feature["properties"]["tags"]["landuse"] == "forest":
            ror_tobj_file.add_tree(osm_data, feature, 0.50, 1.40, -10, "tree.mesh", "tree.mesh")
            ror_tobj_file.add_grass(osm_data, feature, "grass1")
            feature["properties"]["tags"].pop("landuse")
            return True
        if feature["properties"]["tags"]["landuse"] == "orchard":
            ror_tobj_file.add_tree(osm_data, feature, 1.0, 1.0, 15, "tree2.mesh", "tree2.mesh")
            feature["properties"]["tags"].pop("landuse")
            return True

    if "natural" in feature["properties"]["tags"]:
        if feature["properties"]["tags"]["natural"] == "sand" or feature["properties"]["tags"]["natural"] == "beach":
            ogre_map_surface.draw_sand_feature(osm_data, feature)
            feature["properties"]["tags"].pop("natural")
            return True
        if feature["properties"]["tags"]["natural"] == "grassland" or feature["properties"]["tags"]["natural"] == "scrub":
            ogre_map_surface.draw_grass_feature(osm_data, feature)
            ror_tobj_file.add_grass(osm_data, feature, "grass4")
            feature["properties"]["tags"].pop("natural")
            return True
        if feature["properties"]["tags"]["natural"] == "wood" or feature["properties"]["tags"]["natural"] == "tree_group":
            ror_tobj_file.add_tree(osm_data, feature, 0.50, 1.40, -20, "tree.mesh", "tree.mesh")
            feature["properties"]["tags"].pop("natural")
            return True

        if feature["properties"]["tags"]["natural"] == "shingle":
            ogre_map_surface.draw_sand_feature(osm_data, feature)
            feature["properties"]["tags"].pop("natural")
            return True

    if "place" in feature["properties"]["tags"]:
        if feature["properties"]["tags"]["place"] == "square":
            ogre_map_surface.draw_asphalt_feature(osm_data, feature)
            # square are asphalt by default for now, so just remove surface tags in this case.
            if "surface" in feature["properties"]["tags"] and feature["properties"]["tags"]["surface"] == "asphalt":
                feature["properties"]["tags"].pop("surface")
            feature["properties"]["tags"].pop("place")
            return True
        if feature["properties"]["tags"]["place"] == "islet":
            ogre_map_height.draw_feature(osm_data, feature, config.data["ground_line"], config.data["water_depth"])
            feature["properties"]["tags"].pop("place")
            return True
        # It doesn't seem a good idea to render this:
        # if feature["properties"]["tags"]["place"] == "neighbourhood":
        #    ogre_map_surface.draw_asphalt_feature(osm_data, entity)
        #    feature["properties"]["tags"].pop("place")
        #    return True

    if "tourism" in feature["properties"]["tags"]:
        if feature["properties"]["tags"]["tourism"] == "camp_site":
            ogre_map_surface.draw_grass_feature(osm_data, feature)
            feature["properties"]["tags"].pop("tourism")
            return True
        if feature["properties"]["tags"]["tourism"] == "picnic_site":
            ogre_map_surface.draw_grass_feature(osm_data, feature)
            feature["properties"]["tags"].pop("tourism")
            return True

    if "surface" in feature["properties"]["tags"]:
        if feature["properties"]["tags"]["surface"] == "compacted" and len(feature["properties"]["tags"]) == 1:  # "surface" is the only tag
            ogre_map_surface.draw_sand_feature(osm_data, feature)
            feature["properties"]["tags"].pop("surface")
            return True

    return False
