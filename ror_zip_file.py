import bbox
from gvar import EXPORT_PATH
from helper import lat_lon_to_distance
import os
from zipfile import ZipFile
import shutil
import ror_terrn2_file
import config

otc_file_name = config.data["work_path"] + config.data["map_name"] + ".otc"
page_otc_file_name = config.data["work_path"] + config.data["map_name"] + "-page-0-0.otc"
tobj_file_name = config.data["work_path"] + config.data["map_name"] + ".tobj"
os_file_name = config.data["work_path"] + config.data["map_name"] + ".os"


def create_default_file():
    map_height = lat_lon_to_distance(bbox.coord["north"], bbox.coord["south"], bbox.coord["east"], bbox.coord["east"])
    map_width = lat_lon_to_distance(bbox.coord["north"], bbox.coord["north"], bbox.coord["west"], bbox.coord["east"])
    print("Map size: ", map_width, "x", map_height)

    shutil.rmtree(config.data["work_path"], ignore_errors=True)
    os.makedirs(config.data["work_path"], exist_ok=True)
    shutil.rmtree(config.data["log_path"], ignore_errors=True)
    os.makedirs(config.data["log_path"], exist_ok=True)

    with open(otc_file_name, "w") as otc_file:
        otc_file.write("Pages_X=0 \n\
Pages_Y=0 \n\
Flat=1 \n\
WorldSizeX=" + str(int(map_height)) + "\n\
WorldSizeZ=" + str(int(map_width)) + "\n\
WorldSizeY=0\n\
PageFileFormat=" + config.data["map_name"] + "-page-0-0.otc" + "\n\
LayerBlendMapSize=128\n\
disableCaching=0\n\
minBatchSize=17\n\
maxBatchSize=65\n\
LightmapEnabled=0\n\
NormalMappingEnabled=1\n\
SpecularMappingEnabled=1\n\
ParallaxMappingEnabled=0\n\
GlobalColourMapEnabled=0\n\
ReceiveDynamicShadowsDepth=0\n\
CompositeMapSize=1024\n\
CompositeMapDistance=4000\n\
SkirtSize=30\n\
LightMapSize=1024\n\
CastsDynamicShadows=0\n\
MaxPixelError=5\n\
DebugBlendMaps=0\n")

    ror_terrn2_file.create_file(map_width, map_height)

    with open(page_otc_file_name, "w") as page_otc_file:
        page_otc_file.write(
            config.data["map_name"] + ".png\n1\n4    , asphalt_diffusespecular.dds      ,    asphalt_normalheight.dds\n")

    with open(tobj_file_name, "w") as tobj_file:
        tobj_file.write("\n")

    with open(os_file_name, "w") as file:
        file.write("caelum_sky_system " + config.data["map_name"] + ".os\n{\njulian_day 180.85\ntime_scale 1\nlongitude " + str(bbox.coord[
            "west"]) + "\nlatitude " + str(bbox.coord["north"]) + "\nmanage_ambient_light true\nminimum_ambient_light 0.06 0.08 0.12\n\
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
    with ZipFile(EXPORT_PATH + config.data["map_name"] + ".zip", 'w') as zip_object:
        zip_object.write(otc_file_name, arcname=config.data["map_name"] + ".otc")
        zip_object.write(page_otc_file_name, arcname=config.data["map_name"] + "-page-0-0.otc")
        zip_object.write(os_file_name, arcname=config.data["map_name"] + ".os")
        zip_object.write(config.data["work_path"] + config.data["map_name"] + ".terrn2", arcname=config.data["map_name"] + ".terrn2")
        for file in all_files:
            zip_object.write(config.data["resource_path"] + file,
                             arcname=file)


def add_file(file_name_to_add):
    with ZipFile(EXPORT_PATH + config.data["map_name"] + ".zip", 'a') as zip_object:
        zip_object.write(config.data["work_path"] + file_name_to_add, arcname=file_name_to_add)
