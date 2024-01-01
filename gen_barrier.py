import object_3d
import config


def process(osm_data):
    print("Generating barriers")
    for way in osm_data.ways:
        if "barrier" in way.tags:
            if way.tags["barrier"] == "wall":
                object_3d.create_all_object_file(way.nodes, height=config.data["barrier_height"],
                                                 wall_texture="mapgen_dark_grey", roof_texture="mapgen_dark_grey",
                                                 is_barrier=True)
                way.tags.pop("barrier")
