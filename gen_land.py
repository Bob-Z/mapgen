import ogre_map_surface
import ogre_map_vegetation
import ror_tobj_file


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
            else:
                ogre_map_surface.draw_grass_entity(osm_data, entity)
            entity.tags.pop("leisure")
            return True
        if entity.tags["leisure"] == "playground":
            if "surface" in entity.tags and entity.tags["surface"] == "compacted":
                ogre_map_surface.draw_gravel_entity(osm_data, entity)
                entity.tags.pop("surface")
            else:
                ogre_map_surface.draw_grass_entity(osm_data, entity)
            entity.tags.pop("leisure")
            return True

    if "natural" in entity.tags:
        if entity.tags["natural"] == "sand":
            ogre_map_surface.draw_sand_entity(osm_data, entity)
            entity.tags.pop("natural")
            return True
        if entity.tags["natural"] == "beach":
            ogre_map_surface.draw_sand_entity(osm_data, entity)
            entity.tags.pop("natural")
            return True
        if entity.tags["natural"] == "grassland":
            ogre_map_surface.draw_grass_entity(osm_data, entity)
            entity.tags.pop("natural")
            return True
        if entity.tags["natural"] == "scrub":
            ogre_map_surface.draw_grass_entity(osm_data, entity)
            entity.tags.pop("natural")
            return True

    if "landuse" in entity.tags:
        if entity.tags["landuse"] == "grass" or entity.tags["landuse"] == "recreation_ground":
            ogre_map_surface.draw_grass_entity(osm_data, entity)
            entity.tags.pop("landuse")
            return True
        if entity.tags["landuse"] == "construction" or entity.tags["landuse"] == "industrial" or entity.tags[
            "landuse"] == "residential" or entity.tags["landuse"] == "retail":
            ogre_map_surface.draw_asphalt_entity(osm_data, entity)
            entity.tags.pop("landuse")
            return True
        if entity.tags["landuse"] == "forest":
            ror_tobj_file.add_tree(osm_data, entity, -10, "tree.mesh", "tree.mesh")
            entity.tags.pop("landuse")
            return True

    if "place" in entity.tags:
        if entity.tags["place"] == "square":
            ogre_map_surface.draw_asphalt_entity(osm_data, entity)
            # square are asphalt by default for now, so just remove surface tags in this case.
            if "surface" in entity.tags and entity.tags["surface"] == "asphalt":
                entity.tags.pop("surface")
            entity.tags.pop("place")
            return True

    return False
