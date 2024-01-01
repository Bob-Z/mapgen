import object_3d
import config
import gvar


def process(osm_data):
    # z = -gvar.GROUND_LEVEL  -> to be sure that lands starts at the bottom of the sea
    for way in osm_data.ways:
        if "landuse" in way.tags:
            if way.tags["landuse"] == "grass":
                object_3d.create_all_object_file(way.nodes, height=gvar.GROUND_LEVEL + config.data["grass_height"], z=-gvar.GROUND_LEVEL,
                                                 wall_texture="mapgen_grass", roof_texture="mapgen_grass")
                way.tags.pop("landuse")

        elif "leisure" in way.tags:
            if way.tags["leisure"] == "park":
                object_3d.create_all_object_file(way.nodes, height=gvar.GROUND_LEVEL + config.data["grass_height"], z=-gvar.GROUND_LEVEL,
                                                 wall_texture="mapgen_grass_dandelion", roof_texture="mapgen_grass_dandelion")
                way.tags.pop("leisure")

        elif "natural" in way.tags:
            if way.tags["natural"] == "sand":
                object_3d.create_all_object_file(way.nodes, height=gvar.GROUND_LEVEL + config.data["sand_height"], z=-gvar.GROUND_LEVEL,
                                                 wall_texture="mapgen_yellow_sand", roof_texture="mapgen_yellow_sand")

                way.tags.pop("natural")
            elif way.tags["natural"] == "beach":
                if "surface" in way.tags:
                    if way.tags["surface"] == "sand":
                        object_3d.create_all_object_file(way.nodes, height=gvar.GROUND_LEVEL + config.data["sand_height"], z=-gvar.GROUND_LEVEL,
                                                         wall_texture="mapgen_yellow_sand",
                                                         roof_texture="mapgen_yellow_sand")

                        way.tags.pop("natural")
                        way.tags.pop("surface")
            # sand by default
            else:
                object_3d.create_all_object_file(way.nodes, height=gvar.GROUND_LEVEL + config.data["sand_height"], z=-gvar.GROUND_LEVEL,
                                                 wall_texture="mapgen_yellow_sand",
                                                 roof_texture="mapgen_yellow_sand")
                way.tags.pop("natural")
