import PIL.Image
import PIL.ImageDraw
import PIL.ImageFilter
import config
import ror_zip_file
import ogre_map_helper

all_image = {}


def init():
    pass


def draw_vegetation_map(name, osm_data, entity, density):
    if name not in all_image:
        all_image[name] = PIL.Image.new(mode="L", size=(
            int(config.data["map_size"] / config.data["map_precision"]),
            int(config.data["map_size"] / config.data["map_precision"])),
                                        color=0)

    image = all_image[name]
    my_draw = PIL.ImageDraw.Draw(image)

    ogre_map_helper.draw_entity(my_draw, osm_data, entity, outer_height=density, inner_height=0)

    return get_file_name(name)


def create_file(all_road_coord):
    draw_road(all_road_coord)
    global all_image
    for key, image in all_image.items():
        image.save(config.data["work_path"] + get_file_name(key), "PNG")

        ror_zip_file.add_to_zip_file_list(get_file_name(key))


def get_file_name(key):
    return "vegetation_" + key + ".png"


def draw_road(all_road_data):
    global all_image
    for key, image in all_image.items():
        my_draw = PIL.ImageDraw.Draw(image)
        for road_data in all_road_data:
            line = []
            max_road_size = 0.0
            for data in road_data:
                split_data = data.split(", ")
                line.append((float(split_data[0]) / config.data["map_precision"],
                             float(split_data[2]) / config.data["map_precision"]))
                road_size = float(split_data[6]) + float(split_data[7])
                if road_size < road_size:
                    max_road_size = split_data[6] + split_data[7]

            my_draw.line(line, fill=0, width=int(config.data["no_vegetation_for_road_size"] / config.data["map_precision"]),
                         joint="curve")
