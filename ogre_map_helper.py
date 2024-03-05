import ogre_map_height
import osm
import helper


def draw_entity(draw, osm_data, entity, outer_height, inner_height=None):
    outer_color = ogre_map_height.height_to_color(outer_height)
    if inner_height is not None:
        inner_color = ogre_map_height.height_to_color(inner_height)

    if hasattr(entity, "members"):
        for member in entity.members:
            if member.role == "outer":
                way = osm.get_way_by_id(osm_data, member.ref)
                if way is not None:
                    coord = helper.node_to_map_coord(way.nodes)
                    draw.polygon(coord, fill=outer_color, outline=None, width=1)
        for member in entity.members:
            if member.role == "inner":
                way = osm.get_way_by_id(osm_data, member.ref)
                if way is not None:
                    coord = helper.node_to_map_coord(way.nodes)
                    draw.polygon(coord, fill=inner_color, outline=None, width=1)

    else:
        coord = helper.node_to_map_coord(entity.nodes)
        draw.polygon(coord, fill=outer_color, outline=None, width=1)


def draw_polygon(draw, polygon, color):
    draw.polygon(polygon, fill=color, outline=None, width=1)
