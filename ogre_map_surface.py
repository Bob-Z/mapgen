import PIL.Image
import PIL.ImageDraw
import PIL.ImageFilter
import config
import ror_zip_file
import ogre_map_height
import ogre_map_helper
import osm
import helper
import gvar

surf = []
draw = []


def init():
    global surf
    global draw

    for n in range(5):
        surf.append(PIL.Image.new(mode="RGB", size=(
            int(gvar.map_size / gvar.map_precision), int(gvar.map_size / gvar.map_precision)),
                                  color=(0, 0, 0)))
        draw.append(PIL.ImageDraw.Draw(surf[n]))


def draw_asphalt_entity(osm_data, entity):
    draw_entity(0, osm_data, entity, (255, 0, 0))


def draw_rock_entity(osm_data, entity):
    draw_entity(1, osm_data, entity, (255, 0, 0))


def draw_sand_entity(osm_data, entity):
    draw_entity(2, osm_data, entity, (255, 0, 0))


def draw_grass_entity(osm_data, entity):
    draw_entity(3, osm_data, entity, (255, 0, 0))


def draw_gravel_entity(osm_data, entity):
    # RoR currently ignore the last blendmap when shadows are activated. So we fall back to another surface (4 -> 2)
    # draw_entity(4, osm_data, entity, (255, 0, 0))
    draw_entity(2, osm_data, entity, (255, 0, 0))


def draw_entity(surf_index, osm_data, entity, color):
    ogre_map_helper.draw_entity(draw[surf_index], osm_data, entity, outer_color=color, inner_color=(0, 0, 0))


def draw_polygon(surf_index, polygon, color):
    draw[surf_index].polygon(polygon, fill=color, outline=None, width=1)


def create_file():
    global surf

    for n in range(5):
        blur_im = surf[n].filter(PIL.ImageFilter.GaussianBlur(ogre_map_height.BLUR_RADIUS))
        blur_im.save(config.data["work_path"] + "surface" + str(n) + ".png", "PNG")

        ror_zip_file.add_to_zip_file_list("surface" + str(n) + ".png")
