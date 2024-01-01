import object_3d
import config


def process(osm_data):
    print("Generating buildings")
    for way in osm_data.ways:
        level_qty = 1
        if "building:levels" in way.tags:
            level_qty = way.tags["building:levels"]
            way.tags.pop("building:levels")
        height = float(level_qty) * config.data["building_level_height"]

        if "amenity" in way.tags:
            if way.tags["amenity"] == "shelter":
                object_3d.create_all_object_file(way.nodes, height, wall_texture="mapgen_red",
                                                 roof_texture="mapgen_red")

                way.tags.pop("amenity")

        elif "building" in way.tags:
            object_3d.create_all_object_file(way.nodes, height=height, wall_texture=config.data["wall_texture"],
                                             roof_texture=config.data["roof_texture"],
                                             is_barrier=False, roof_texture_generator=None)
            way.tags.pop("building")
        elif "disused:building" in way.tags:
            object_3d.create_all_object_file(way.nodes, height=height, wall_texture=config.data["wall_texture"],
                                             roof_texture=config.data["roof_texture"],
                                             is_barrier=False, roof_texture_generator=None)
            way.tags.pop("disused:building")
        elif "demolished:building" in way.tags:
            object_3d.create_all_object_file(way.nodes, height=height, wall_texture=config.data["wall_texture"],
                                             roof_texture=config.data["roof_texture"],
                                             is_barrier=False, roof_texture_generator=None)
            way.tags.pop("demolished:building")
