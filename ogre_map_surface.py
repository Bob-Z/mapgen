import PIL.Image
import PIL.ImageDraw
import PIL.ImageFilter
import config
import ror_zip_file
import ogre_map_height
import ogre_map_helper

surf = []
draw = []


def init():
    global surf
    global draw

    for n in range(5):
        surf.append(PIL.Image.new(mode="RGB", size=(
            int(config.data["map_size"] / config.data["map_precision"]),
            int(config.data["map_size"] / config.data["map_precision"])),
                                  color=(0, 0, 0)))
        draw.append(PIL.ImageDraw.Draw(surf[n]))


def draw_asphalt_feature(feature):
    draw_feature(0, feature, (255, 0, 0))


def draw_rock_feature(feature):
    draw_feature(1, feature, (255, 0, 0))


def draw_sand_feature(feature):
    draw_feature(2, feature, (255, 0, 0))


def draw_grass_feature(feature):
    draw_feature(3, feature, (255, 0, 0))


def draw_gravel_feature(feature):
    # RoR currently ignore the last blend map when shadows are activated. So we fall back to another surface (4 -> 2)
    # draw_feature(4, osm_data, feature, (255, 0, 0))
    draw_feature(2,  feature, (255, 0, 0))


def draw_feature(surf_index, feature, color):
    ogre_map_helper.draw_feature(draw[surf_index], feature, outer_color=color, inner_color=(0, 0, 0))


def draw_polygon(surf_index, polygon, color):
    draw[surf_index].polygon(polygon, fill=color, outline=None, width=1)


def create_file():
    global surf

    for n in range(5):
        blur_im = surf[n].filter(PIL.ImageFilter.GaussianBlur(ogre_map_height.BLUR_RADIUS))
        blur_im.save(config.data["work_path"] + "surface" + str(n) + ".png", "PNG")

        ror_zip_file.add_to_zip_file_list("surface" + str(n) + ".png")
