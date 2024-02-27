import object_3d
import config

barrier_tag_value = [['barrier', 'wall'], ['barrier', 'fence']]
barrier_tag = []


def process(way):
    for tag_value in barrier_tag_value:
        if tag_value[0] in way.tags:
            if way.tags[tag_value[0]] == tag_value[1]:
                object_3d.create_all_object_file(way.nodes, height=config.data["barrier_height"],
                                                 wall_texture="mapgen_dark_grey", roof_texture="mapgen_dark_grey",
                                                 is_barrier=True)
                way.tags.pop(tag_value[0])
                return True

    for tag in barrier_tag:
        if tag in way.tags:
            object_3d.create_all_object_file(way.nodes, height=config.data["barrier_height"],
                                             wall_texture="mapgen_dark_grey", roof_texture="mapgen_dark_grey",
                                             is_barrier=True)
            way.tags.pop(tag)
            return True

    return False
