import object_3d
import config
import osm

barrier_tag_value = [
    ['barrier', 'wall', "mapgen_dark_grey", config.data["default_wall_texture"], config.data["barrier_width"]],
    ['barrier', 'fence', "mapgen_dark_grey", config.data["default_fence_texture"], config.data["barrier_width"]],
    ['barrier', 'hedge', config.data["hedge_texture"], config.data["default_hedge_texture"], config.data["hedge_width"]]
    # ['barrier', 'gate',...
    # ['barrier', 'lift_gate',...
    # ['barrier', 'retaining_wall',...
    # ['barrier', 'kerb',...
]

barrier_tag = []


def process(way):
    for tag_value in barrier_tag_value:
        if tag_value[0] in way.tags:
            if way.tags[tag_value[0]] == tag_value[1]:
                height, min_height, roof_height = osm.get_height(way)
                if height is None:
                    height = config.data["barrier_height"]

                texture = ogre_material.create_material(random.choice(tag_value[3]), tags)
                if texture is None:
                    texture = tag_value[2]

                object_3d.create_all_object_file(way.nodes, height=height,
                                                 wall_texture=texture, top_texture=texture,
                                                 is_barrier=True, barrier_width=tag_value[4])
                way.tags.pop(tag_value[0])
                return True

    for tag in barrier_tag:
        if tag in way.tags:
            height = osm.get_height(way)
            if height is None:
                height = config.data["barrier_height"]

            texture = ogre_material.create_material(random.choice(tag_value[3]), tags)
            if texture is None:
                texture = tag_value[2]

            object_3d.create_all_object_file(way.nodes, height=height,
                                             wall_texture=texture, top_texture=texture,
                                             is_barrier=True)
            way.tags.pop(tag)
            return True

    return False
