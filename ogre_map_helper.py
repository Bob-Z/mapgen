import ogre_map_height
import osm
import helper
import config


def draw_entity(draw, osm_data, entity, outer_height=None, inner_height=None, outer_color=None, inner_color=None):
    my_outer_color = outer_color
    my_inner_color = inner_color
    if outer_height is not None:
        my_outer_color = ogre_map_height.height_to_color(outer_height)
        if inner_height is not None:
            my_inner_color = ogre_map_height.height_to_color(inner_height)
        else:
            my_inner_color = ogre_map_height.height_to_color(config.data["ground_line"])

    if hasattr(entity, "members"):
        outer_coord = []

        # draw None or outer first
        for member in entity.members:
            if member.role == "inner":
                continue
            way = osm.get_way_by_id(osm_data, member.ref)
            if way is not None:
                outer_coord.append(way.nodes)

        if len(outer_coord) > 0:
            all_coord = helper.node_to_map_coord(osm.concat_way_by_distance(outer_coord))

            draw.polygon(all_coord, fill=my_outer_color, outline=None, width=1)

        # then draw inner
        for member in entity.members:
            if member.role == "inner":
                way = osm.get_way_by_id(osm_data, member.ref)
                if way is not None:
                    coord = helper.node_to_map_coord(way.nodes)
                    draw.polygon(coord, fill=my_inner_color, outline=None, width=1)

    else:
        coord = helper.node_to_map_coord(entity.nodes)
        draw.polygon(coord, fill=my_outer_color, outline=None, width=1)


def draw_polygon(draw, polygon, color):
    draw.polygon(polygon, fill=color, outline=None, width=1)
