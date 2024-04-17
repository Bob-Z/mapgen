import PIL.Image
import PIL.ImageDraw
import PIL.ImageFilter
import config
import ror_zip_file
import ogre_otc_file
import ogre_map_height
import ogre_map_helper
import gvar

MAX_COLOR = 0xff  # Because we use 8 bits PNG
BLUR_RADIUS = 1

im = None
draw = None
unblurred_entity = []


def height_to_color(height):
    return int(MAX_COLOR * height / ogre_otc_file.MAX_HEIGHT)


def init():
    global im
    global draw

    im = PIL.Image.new(mode="L", size=(
        int(gvar.map_size / gvar.map_precision),
        int(gvar.map_size / gvar.map_precision)),
                       color=ogre_map_height.MAX_COLOR)  # color=MAX_COLOR fill the map with height defined by WorldSizeY parameter in otc file

    draw = PIL.ImageDraw.Draw(im)


def set_map_height(height):
    global im
    im.paste(ogre_map_height.height_to_color(height), (0, 0, im.size[0], im.size[1]))


def draw_entity(osm_data, entity, outer_height, inner_height=None, draw_object=None):
    global draw
    if draw_object is None:
        draw_object = draw
    ogre_map_helper.draw_entity(draw_object, osm_data, entity, outer_height=outer_height, inner_height=inner_height)

def draw_entity_unblurred(osm_data, entity, outer_height, inner_height=None):
    unblurred_entity.append((osm_data, entity, outer_height, inner_height))


def draw_polygon(polygon, color):
    if gvar.map_precision != 1.0:
        new_polygon = []
        for c in polygon:
            new_polygon.append((c[0] / gvar.map_precision, c[1] / gvar.map_precision))
        polygon = new_polygon
    ogre_map_helper.draw_polygon(draw, polygon, color)


def create_file():
    global im
    blur_im = im.filter(PIL.ImageFilter.GaussianBlur(ogre_map_height.BLUR_RADIUS))
    unblurred_draw = PIL.ImageDraw.Draw(blur_im)

    for entity in unblurred_entity:
        draw_entity(entity[0], entity[1], entity[2], entity[3], draw_object=unblurred_draw)

    blur_im.save(config.data["work_path"] + config.data["map_name"] + "_height.png", "PNG")
    ror_zip_file.add_to_zip_file_list(config.data["map_name"] + "_height.png")
