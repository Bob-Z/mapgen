import PIL.Image
import PIL.ImageDraw
import PIL.ImageFilter
import config
import ror_zip_file
import ogre_map_height
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
    draw_entity(4, osm_data, entity, (255, 0, 0))


def draw_entity(surf_index, osm_data, entity, color):
    global draw
    if hasattr(entity, "members"):
        for member in entity.members:
            way = osm.get_way_by_id(osm_data, member.ref)
            if way is not None:
                coord = helper.node_to_map_coord(way.nodes)
                if member.role == "outer":
                    draw[surf_index].polygon(coord, fill=color, outline=None, width=1)
                elif member.role == "inner":
                    draw[surf_index].polygon(coord, fill=(0, 0, 0), outline=None, width=1)
    else:
        coord = helper.node_to_map_coord(entity.nodes)
        draw[surf_index].polygon(coord, fill=color, outline=None, width=1)


def draw_polygon(surf_index, polygon, color):
    draw[surf_index].polygon(polygon, fill=color, outline=None, width=1)


def create_file():
    global surf

    for n in range(5):
        blur_im = surf[n].filter(PIL.ImageFilter.GaussianBlur(ogre_map_height.BLUR_RADIUS))
        blur_im.save(config.data["work_path"] + "surface" + str(n) + ".png", "PNG")

        ror_zip_file.add_to_zip_file_list("surface" + str(n) + ".png")
