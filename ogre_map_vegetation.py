import PIL.Image
import PIL.ImageDraw
import PIL.ImageFilter
import config
import ror_zip_file
import ogre_map_helper
import gvar

index = 0


def init():
    pass


def add_vegetation_map(osm_data, entity, density):
    global index

    surf = PIL.Image.new(mode="L", size=(
        int(gvar.map_size / gvar.map_precision),
        int(gvar.map_size / gvar.map_precision)),
                         color=0)

    my_draw = PIL.ImageDraw.Draw(surf)

    ogre_map_helper.draw_entity(my_draw, osm_data, entity, outer_height=density, inner_height=0)

    file_name = "vegetation" + str(index) + ".png"
    surf.save(config.data["work_path"] + file_name, "PNG")

    ror_zip_file.add_to_zip_file_list(file_name)

    index += 1

    return file_name
