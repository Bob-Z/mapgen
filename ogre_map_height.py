import PIL.Image
import PIL.ImageDraw
import PIL.ImageFilter
import config
import ror_zip_file
import ogre_otc_file
import ogre_map_height
import osm
import helper

MAX_COLOR = 0xff  # Because we use 8 bits PNG
MAP_HEIGHT_SIZE_FACTOR = 1
BLUR_RADIUS = 1

im = None
draw = None


def height_to_color(height):
    return int(MAX_COLOR * height / ogre_otc_file.MAX_HEIGHT)


def init(map_size):
    global im
    global draw

    im = PIL.Image.new(mode="L", size=(
        int(map_size) * ogre_map_height.MAP_HEIGHT_SIZE_FACTOR, int(map_size) * ogre_map_height.MAP_HEIGHT_SIZE_FACTOR),
                       color=ogre_map_height.MAX_COLOR)  # color=MAX_COLOR fill the map with height defined by WorldSizeY parameter in otc file

    draw = PIL.ImageDraw.Draw(im)


def set_map_height(height):
    global im
    im.paste(ogre_map_height.height_to_color(height), (0, 0, im.size[0], im.size[1]))


def draw_entity(osm_data, entity, outer_height, inner_height=None):
    outer_color = ogre_map_height.height_to_color(outer_height)
    if inner_height is not None:
        inner_color = ogre_map_height.height_to_color(inner_height)

    if hasattr(entity, "members"):
        for member in entity.members:
            way = osm.get_way_by_id(osm_data, member.ref)
            if way is not None:
                coord = helper.node_to_map_coord(way.nodes)
                if member.role == "outer":
                    draw.polygon(coord, fill=outer_color, outline=None, width=1)
                elif member.role == "inner":
                    draw.polygon(coord, fill=inner_color, outline=None, width=1)
    else:
        coord = helper.node_to_map_coord(entity.nodes)
        draw.polygon(coord, fill=outer_color, outline=None, width=1)


def draw_polygon(polygon, color):
    draw.polygon(polygon, fill=color, outline=None, width=1)


def create_file():
    global im
    blur_im = im.filter(PIL.ImageFilter.GaussianBlur(ogre_map_height.BLUR_RADIUS))
    blur_im.save(config.data["work_path"] + config.data["map_name"] + "_height.png", "PNG")
    ror_zip_file.add_to_zip_file_list(config.data["map_name"] + "_height.png")
