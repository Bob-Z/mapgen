import object_3d
import config
import gvar
import osm


def process(osm_data):
    print("Generating lands")
    # z = -gvar.GROUND_LEVEL  -> to be sure that lands starts at the bottom of the sea
    for way in osm_data.ways:
        # if "landuse" in way.tags:
        #    if way.tags["landuse"] == "grass":
        #        object_3d.create_all_object_file(way.nodes, height=gvar.GROUND_LEVEL + config.data["grass_height"], z=-gvar.GROUND_LEVEL,
        #                                         wall_texture="mapgen_grass", roof_texture="mapgen_grass")
        #        way.tags.pop("landuse")

        if "leisure" in way.tags:
            if way.tags["leisure"] == "park":
                object_3d.create_all_object_file(way.nodes, height=gvar.GROUND_LEVEL + config.data["grass_height"],
                                                 z=-gvar.GROUND_LEVEL,
                                                 wall_texture="mapgen_grass_dandelion",
                                                 roof_texture="mapgen_grass_dandelion")
                way.tags.pop("leisure")

        elif "natural" in way.tags:
            if way.tags["natural"] == "sand":
                object_3d.create_all_object_file(way.nodes, height=gvar.GROUND_LEVEL + config.data["sand_height"],
                                                 z=-gvar.GROUND_LEVEL,
                                                 wall_texture="mapgen_yellow_sand", roof_texture="mapgen_yellow_sand")

                way.tags.pop("natural")
            elif way.tags["natural"] == "beach":
                if "surface" in way.tags:
                    if way.tags["surface"] == "sand":
                        object_3d.create_all_object_file(way.nodes,
                                                         height=gvar.GROUND_LEVEL + config.data["sand_height"],
                                                         z=-gvar.GROUND_LEVEL,
                                                         wall_texture="mapgen_yellow_sand",
                                                         roof_texture="mapgen_yellow_sand")

                        way.tags.pop("natural")
                        way.tags.pop("surface")
            elif way.tags["natural"] == "scrub":
                object_3d.create_all_object_file(way.nodes, height=gvar.GROUND_LEVEL + config.data["scrub_height"],
                                                 z=-gvar.GROUND_LEVEL,
                                                 wall_texture="mapgen_scrub", roof_texture="mapgen_scrub")

                way.tags.pop("natural")

    for rel in osm_data.relations:
        if "natural" in rel.tags:
            if rel.tags["natural"] == "scrub":
                for member in rel.members:
                    way = osm.get_way_by_id(osm_data, member.ref)
                    if way is not None:
                        if member.role == "outer":
                            object_3d.create_all_object_file(way.nodes, height=config.data["scrub_height"],
                                                             wall_texture="mapgen_scrub",
                                                             roof_texture="mapgen_scrub")
                        elif member.role == "inner":
                            object_3d.create_all_object_file(way.nodes, height=config.data["island_height"],
                                                             wall_texture="mapgen_beige",
                                                             roof_texture="mapgen_beige")
                rel.tags.pop("natural")
                rel.tags.pop("type")  # FIXME is this always multipolygon ?

            elif rel.tags["natural"] == "sand" or rel.tags["natural"] == "beach":
                for member in rel.members:
                    way = osm.get_way_by_id(osm_data, member.ref)
                    if way is not None:
                        if member.role == "outer":
                            object_3d.create_all_object_file(way.nodes, height=config.data["sand_height"],
                                                             wall_texture="mapgen_yellow_sand",
                                                             roof_texture="mapgen_yellow_sand")
                        elif member.role == "inner":
                            object_3d.create_all_object_file(way.nodes, height=config.data["island_height"],
                                                             wall_texture="mapgen_beige",
                                                             roof_texture="mapgen_beige")
                rel.tags.pop("natural")
                rel.tags.pop("type")  # FIXME is this always multipolygon ?
