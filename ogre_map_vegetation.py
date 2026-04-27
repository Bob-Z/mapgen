import PIL.Image
import PIL.ImageDraw
import PIL.ImageFilter
import config
import ror_zip_file
import ogre_map_helper
import gvar

all_image = {}


def init():
    pass


def draw_vegetation_map(name, osm_data, entity, density):
    if name not in all_image:
        all_image[name] = PIL.Image.new(mode="L", size=(
            int(gvar.map_size / gvar.map_precision),
            int(gvar.map_size / gvar.map_precision)),
                                        color=0)

    image = all_image[name]
    my_draw = PIL.ImageDraw.Draw(image)

    ogre_map_helper.draw_entity(my_draw, osm_data, entity, outer_height=density, inner_height=0)

    return get_file_name(name)


def create_file():
    global all_image
    for key, image in all_image.items():
        image.save(config.data["work_path"] + get_file_name(key), "PNG")

        ror_zip_file.add_to_zip_file_list(get_file_name(key))


def get_file_name(key):
    return "vegetation_" + key + ".png"
