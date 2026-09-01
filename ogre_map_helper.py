import ogre_map_height
import osm
import helper
import config


def draw_feature(draw, feature, outer_height=None, inner_height=None, outer_color=None, inner_color=None):
    my_outer_color = outer_color
    my_inner_color = inner_color
    if outer_height is not None:
        my_outer_color = ogre_map_height.height_to_color(outer_height)
        if inner_height is not None:
            my_inner_color = ogre_map_height.height_to_color(inner_height)
        else:
            my_inner_color = ogre_map_height.height_to_color(config.data["ground_line"])

    all_all_coord = osm.get_coord_from_feature(feature)

    color = my_outer_color
    for all_coord in all_all_coord:
        all_map_coord = helper.all_coord_to_map_coord(all_coord)
        draw.polygon(all_map_coord, fill=color, outline=None, width=1)
        color = my_inner_color


def draw_polygon(draw, polygon, color):
    draw.polygon(polygon, fill=color, outline=None, width=1)
