import ogre_map_height
import osm
import helper
import config


def draw_feature(draw, osm_data, feature, outer_height=None, inner_height=None, outer_color=None, inner_color=None):
    my_outer_color = outer_color
    my_inner_color = inner_color
    if outer_height is not None:
        my_outer_color = ogre_map_height.height_to_color(outer_height)
        if inner_height is not None:
            my_inner_color = ogre_map_height.height_to_color(inner_height)
        else:
            my_inner_color = ogre_map_height.height_to_color(config.data["ground_line"])

    first_coord = True  # FIXME Is first coord always the outer one ?
    all_all_coord = osm.get_coord_from_feature(feature)
    for all_coord in all_all_coord:
        all_map_coord = helper.coord_to_map_coord(all_coord)
        if first_coord is True:
            fill_color = my_outer_color
            first_coord = False
        else:
            fill_color = my_inner_color

        draw.polygon(all_map_coord, fill=fill_color, outline=None, width=1)


def draw_polygon(draw, polygon, color):
    draw.polygon(polygon, fill=color, outline=None, width=1)
