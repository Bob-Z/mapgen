import object_3d
import config
import osm
import ogre_material

barrier_tag_value = [
    ['barrier', 'wall', None, "mapgen_dark_grey", None, "mapgen_dark_grey", config.data["barrier_width"]],
    ['barrier', 'fence', None, "mapgen_dark_grey", None, "mapgen_dark_grey", config.data["barrier_width"]],
    ['barrier', 'hedge', ogre_material.create_material_hedge, None, None, "mapgen_hedge",
     config.data["hedge_width"]]
]

barrier_tag = []


def process(way):
    for tag_value in barrier_tag_value:
        if tag_value[0] in way.tags:
            if way.tags[tag_value[0]] == tag_value[1]:
                height, min_height = osm.get_height(way)
                if height is None:
                    height = config.data["barrier_height"]
                object_3d.create_all_object_file(way.nodes, height=height,
                                                 wall_texture=tag_value[3], roof_texture=tag_value[5],
                                                 wall_texture_generator=tag_value[2],
                                                 roof_texture_generator=tag_value[4],
                                                 is_barrier=True, barrier_width=tag_value[6])
                way.tags.pop(tag_value[0])
                return True

    for tag in barrier_tag:
        if tag in way.tags:
            height = osm.get_height(way)
            if height is None:
                height = config.data["barrier_height"]
            object_3d.create_all_object_file(way.nodes, height=height,
                                             wall_texture="mapgen_dark_grey", roof_texture="mapgen_dark_grey",
                                             is_barrier=True)
            way.tags.pop(tag)
            return True

    return False
