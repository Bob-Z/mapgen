import object_3d
import config
import ogre_material
import osm

barrier_tag_value = [
    ['barrier', 'wall', "mapgen_dark_grey", config.data["default_wall_texture"], config.data["barrier_width"]],
    ['barrier', 'fence', "mapgen_dark_grey", config.data["default_fence_texture"], config.data["barrier_width"]],
    ['barrier', 'hedge', config.data["hedge_texture"], config.data["default_hedge_texture"], config.data["hedge_width"]]
]

barrier_tag = []


def process(feature):
    for tag_value in barrier_tag_value:
        if tag_value[0] in feature["properties"]["tags"]:
            if feature["properties"]["tags"][tag_value[0]] == tag_value[1]:
                height, min_height, roof_height = osm.get_height(feature)
                if height is None:
                    height = config.data["barrier_height"]

                texture = ogre_material.create_material(tag_value[3], feature["properties"]["tags"])
                if texture is None:
                    texture = tag_value[2]

                object_3d.create_all_object_file(osm.get_coord_from_feature(feature), height=height,
                                                 wall_texture=texture, top_texture=texture,
                                                 is_barrier=True, barrier_width=tag_value[4])
                feature["properties"]["tags"].pop(tag_value[0])
                return True

    for tag in barrier_tag:
        if tag in feature["properties"]["tags"]:
            height = osm.get_height(feature)
            if height is None:
                height = config.data["barrier_height"]
            object_3d.create_all_object_file(osm.get_coord_from_feature(feature), height=height,
                                             wall_texture="mapgen_dark_grey", top_texture="mapgen_dark_grey",
                                             is_barrier=True)
            feature["properties"]["tags"].pop(tag)
            return True

    return False
