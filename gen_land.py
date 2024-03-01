import ogre_map_surface
import ror_tobj_file
import ogre_map_height
import config


def process(entity, osm_data=None):
    if "amenity" in entity.tags:
        if entity.tags["amenity"] == "parking":
            ogre_map_surface.draw_asphalt_entity(osm_data, entity)
            entity.tags.pop("amenity")
            return True
    if "leisure" in entity.tags:
        if entity.tags["leisure"] == "park":
            ogre_map_surface.draw_grass_entity(osm_data, entity)
            entity.tags.pop("leisure")
            return True
        if entity.tags["leisure"] == "pitch":
            if "surface" in entity.tags and entity.tags["surface"] == "asphalt":
                ogre_map_surface.draw_asphalt_entity(osm_data, entity)
                entity.tags.pop("surface")
            elif "surface" in entity.tags and entity.tags["surface"] == "clay":
                ogre_map_surface.draw_gravel_entity(osm_data, entity)
                entity.tags.pop("surface")
            else:
                ogre_map_surface.draw_grass_entity(osm_data, entity)
            entity.tags.pop("leisure")
            return True
        if entity.tags["leisure"] == "playground":
            if "surface" in entity.tags and entity.tags["surface"] == "compacted":
                ogre_map_surface.draw_sand_entity(osm_data, entity)
                entity.tags.pop("surface")
            else:
                ogre_map_surface.draw_grass_entity(osm_data, entity)
            entity.tags.pop("leisure")
            return True
        if entity.tags["leisure"] == "sports_centre":
            ogre_map_surface.draw_asphalt_entity(osm_data, entity)
            entity.tags.pop("leisure")
            return True
        if entity.tags["leisure"] == "track":
            if "surface" in entity.tags and entity.tags["surface"] == "compacted":
                ogre_map_surface.draw_sand_entity(osm_data, entity)
                entity.tags.pop("surface")
            else:
                ogre_map_surface.draw_asphalt_entity(osm_data, entity)
            entity.tags.pop("leisure")
            return True

    if "landuse" in entity.tags:
        if entity.tags["landuse"] == "grass" or entity.tags["landuse"] == "recreation_ground":
            ogre_map_surface.draw_grass_entity(osm_data, entity)
            entity.tags.pop("landuse")
            return True
        if entity.tags["landuse"] == "construction" or entity.tags["landuse"] == "industrial" or entity.tags[
            "landuse"] == "residential" or entity.tags["landuse"] == "retail" or entity.tags["landuse"] == "education":
            ogre_map_surface.draw_asphalt_entity(osm_data, entity)
            entity.tags.pop("landuse")
            return True
        if entity.tags["landuse"] == "forest":
            ror_tobj_file.add_tree(osm_data, entity, 0.50, 1.40, -10, "tree.mesh", "tree.mesh")
            entity.tags.pop("landuse")
            return True
        if entity.tags["landuse"] == "orchard":
            ror_tobj_file.add_tree(osm_data, entity, 1.0, 1.0, 15, "tree2.mesh", "tree2.mesh")
            entity.tags.pop("landuse")
            return True

    if "natural" in entity.tags:
        if entity.tags["natural"] == "sand" or entity.tags["natural"] == "beach":
            ogre_map_surface.draw_sand_entity(osm_data, entity)
            entity.tags.pop("natural")
            return True
        if entity.tags["natural"] == "grassland" or entity.tags["natural"] == "scrub":
            ogre_map_surface.draw_grass_entity(osm_data, entity)
            entity.tags.pop("natural")
            return True
        if entity.tags["natural"] == "wood" or entity.tags["natural"] == "tree_group":
            ror_tobj_file.add_tree(osm_data, entity, 0.50, 1.40, -20, "tree.mesh", "tree.mesh")
            entity.tags.pop("natural")
            return True

        if entity.tags["natural"] == "shingle":
            ogre_map_surface.draw_sand_entity(osm_data, entity)
            entity.tags.pop("natural")
            return True

    if "place" in entity.tags:
        if entity.tags["place"] == "square":
            ogre_map_surface.draw_asphalt_entity(osm_data, entity)
            # square are asphalt by default for now, so just remove surface tags in this case.
            if "surface" in entity.tags and entity.tags["surface"] == "asphalt":
                entity.tags.pop("surface")
            entity.tags.pop("place")
            return True
        if entity.tags["place"] == "islet":
            ogre_map_height.draw_entity(osm_data, entity, config.data["ground_line"], config.data["water_depth"])
            entity.tags.pop("place")
            return True
        # It doesn't seem a good idea to render this:
        # if entity.tags["place"] == "neighbourhood":
        #    ogre_map_surface.draw_asphalt_entity(osm_data, entity)
        #    entity.tags.pop("place")
        #    return True

    if "tourism" in entity.tags:
        if entity.tags["tourism"] == "camp_site":
            ogre_map_surface.draw_grass_entity(osm_data, entity)
            entity.tags.pop("tourism")
            return True
        if entity.tags["tourism"] == "picnic_site":
            ogre_map_surface.draw_grass_entity(osm_data, entity)
            entity.tags.pop("tourism")
            return True

    if "surface" in entity.tags:
        if entity.tags["surface"] == "compacted" and len(entity.tags) == 1:  # "surface" is the only tag
            ogre_map_surface.draw_sand_entity(osm_data, entity)
            entity.tags.pop("surface")
            return True

    return False
