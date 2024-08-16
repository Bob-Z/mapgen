import bbox
import ogre_map_height
import ogre_map_surface
import ogre_map_vegetation
import os
from zipfile import ZipFile
import shutil
import ror_terrn2_file
import ogre_otc_file
import ogre_page_otc_file
import config

file_list = []

def create_default_file():
    shutil.rmtree(config.data["work_path"], ignore_errors=True)
    os.makedirs(config.data["work_path"], exist_ok=True)
    shutil.rmtree(config.data["log_path"], ignore_errors=True)
    os.makedirs(config.data["log_path"], exist_ok=True)

    ror_terrn2_file.create_file()

    ogre_map_height.init()
    ogre_map_surface.init()
    ogre_map_vegetation.init()

    ogre_otc_file.create_file()
    ogre_page_otc_file.create_file()

    with open(config.data["work_path"] + config.data["map_name"] + ".tobj", "w") as tobj_file:
        tobj_file.write("\n")

    with open(config.data["work_path"] + config.data["map_name"] + "_vegetation.tobj", "w") as tobj_file:
        tobj_file.write("//trees yawFrom, yawTo, scaleFrom, scaleTo, highDensity, distance1, distance2, meshName colormap densitymap gridspacing collmesh\n")

    with open(config.data["work_path"] + config.data["map_name"] + ".os", "w") as file:
        file.write("caelum_sky_system " + config.data[
            "map_name"] + ".os\n{\njulian_day 180.85\ntime_scale 1\nlongitude " + str(bbox.coord[
                                                                                          "west"]) + "\nlatitude " + str(
            bbox.coord["north"]) + "\nmanage_ambient_light true\nminimum_ambient_light 0.06 0.08 0.12\n\
scene_fog_density_multiplier 10.2\nsun\n{\nambient_multiplier 0.55 0.65 0.70\ndiffuse_multiplier 2.20 2.15 2.00\n\
specular_multiplier 1 1 1\nauto_disable_threshold 0.05\nauto_disable true\n}\n\
point_starfield\n{\nmagnitude_scale 2.51189\nmag0_pixel_size 16\nmin_pixel_size 4\nmax_pixel_size 6\n}\n\
sky_dome\n{\nhaze_enabled no\nsky_gradients_image EarthClearSky2.png\natmosphere_depth_image AtmosphereDepth.png\n}\n\
cloud_system\n{\n\
cloud_layer\n{\nheight 300\ncoverage 0.1\ncloud_uv_factor 20\nnear_fade_dist 5000\nfar_fade_dist 8000\n}\n\
cloud_layer\n{\nheight 500\ncoverage 0.1\ncloud_uv_factor 17\n}\n\
cloud_layer\n{\nheight 800\ncoverage 0.1\ncloud_uv_factor 10\n}\n\
cloud_layer\n{\nheight 2000\ncoverage 0.1\ncloud_uv_factor 6\n}\n\
}\n\
}")


def write_default_file():
    all_files = os.listdir(config.data["resource_path"])
    with ZipFile(config.data["export_path"] + config.data["map_name"] + ".zip", 'w') as zip_object:
        zip_object.write(config.data["work_path"] + config.data["map_name"] + ".otc", arcname=config.data["map_name"] + ".otc")
        zip_object.write(config.data["work_path"] + config.data["map_name"] + "-page-0-0.otc", arcname=config.data["map_name"] + "-page-0-0.otc")
        zip_object.write(config.data["work_path"] + config.data["map_name"] + ".os", arcname=config.data["map_name"] + ".os")
        zip_object.write(config.data["work_path"] + config.data["map_name"] + ".terrn2",
                         arcname=config.data["map_name"] + ".terrn2")
        for file in all_files:
            zip_object.write(config.data["resource_path"] + file,
                             arcname=file)


def add_to_zip_file_list(file_name_to_add):
    file_list.append(file_name_to_add)


def create_zip_file():
    with ZipFile(config.data["export_path"] + config.data["map_name"] + ".zip", 'a') as zip_object:
        for file in file_list:
            zip_object.write(config.data["work_path"] + file, arcname=file)
