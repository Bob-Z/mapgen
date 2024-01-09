import object_3d
import config
import gvar
import osm


def process(entity, osm_data=None):
    # z = -gvar.GROUND_LEVEL  -> to be sure that lands starts at the bottom of the sea
    if "leisure" in entity.tags:
        if entity.tags["leisure"] == "park":
            create_from_entity(osm_data, entity, height=gvar.GROUND_LEVEL + config.data["grass_height"],
                               z=-gvar.GROUND_LEVEL,
                               wall_texture="mapgen_grass_dandelion",
                               roof_texture="mapgen_grass_dandelion")
            entity.tags.pop("leisure")
            return True
        if entity.tags["leisure"] == "pitch":
            create_from_entity(osm_data, entity, height=gvar.GROUND_LEVEL + config.data["grass_height"],
                               z=-gvar.GROUND_LEVEL,
                               wall_texture="mapgen_grass",
                               roof_texture="mapgen_grass")
            entity.tags.pop("leisure")
            return True

    if "natural" in entity.tags:
        if entity.tags["natural"] == "sand":
            create_from_entity(osm_data, entity, height=gvar.GROUND_LEVEL + config.data["sand_height"],
                               z=-gvar.GROUND_LEVEL,
                               wall_texture="mapgen_yellow_sand", roof_texture="mapgen_yellow_sand")

            entity.tags.pop("natural")
            return True
        if entity.tags["natural"] == "beach":
            create_from_entity(osm_data, entity,
                               height=gvar.GROUND_LEVEL + config.data["sand_height"],
                               z=-gvar.GROUND_LEVEL,
                               wall_texture="mapgen_yellow_sand",
                               roof_texture="mapgen_yellow_sand")

            entity.tags.pop("natural")
            return True
        if entity.tags["natural"] == "scrub":
            create_from_entity(osm_data, entity, height=gvar.GROUND_LEVEL + config.data["scrub_height"],
                               z=-gvar.GROUND_LEVEL,
                               wall_texture="mapgen_scrub", roof_texture="mapgen_scrub")
            entity.tags.pop("natural")
            return True

    if "landuse" in entity.tags:
        if entity.tags["landuse"] == "grass":
            create_from_entity(osm_data, entity, height=gvar.GROUND_LEVEL + config.data["grass_height"],
                               z=-gvar.GROUND_LEVEL,
                               wall_texture="mapgen_grass",
                               roof_texture="mapgen_grass")
            entity.tags.pop("landuse")
            return True

    return False


def create_from_entity(osm_data, entity, height, z,
                       wall_texture, roof_texture, island_wall_texture=config.data["ground_texture"],
                       island_roof_texture=config.data["ground_texture"], roof_texture_generator=None):
    if hasattr(entity, "members"):
        for member in entity.members:
            way = osm.get_way_by_id(osm_data, member.ref)
            if way is not None:
                if member.role == "outer":
                    object_3d.create_all_object_file(way.nodes, height=height, z=z,
                                                     wall_texture=wall_texture,
                                                     roof_texture=roof_texture,
                                                     roof_texture_generator=roof_texture_generator)
                elif member.role == "inner":
                    object_3d.create_all_object_file(way.nodes, height=height, z=z,
                                                     wall_texture=island_wall_texture,
                                                     roof_texture=island_roof_texture,
                                                     roof_texture_generator=roof_texture_generator)
    else:
        object_3d.create_all_object_file(entity.nodes, height=height,
                                         z=z,
                                         wall_texture=wall_texture,
                                         roof_texture=roof_texture, roof_texture_generator=roof_texture_generator)
