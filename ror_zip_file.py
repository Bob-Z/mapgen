import bbox
import gvar
from gvar import WORK_PATH
from gvar import RESOURCE_PATH
from gvar import MAP_NAME
from gvar import EXPORT_PATH
from helper import lat_lon_to_distance
import os
from zipfile import ZipFile
import shutil

otc_file_name = WORK_PATH + MAP_NAME + ".otc"
page_otc_file_name = WORK_PATH + MAP_NAME + "-page-0-0.otc"
terrn2_file_name = WORK_PATH + MAP_NAME + ".terrn2"
tobj_file_name = WORK_PATH + MAP_NAME + ".tobj"


def create_default_file():
    map_height = lat_lon_to_distance(bbox.coord["north"], bbox.coord["south"], bbox.coord["east"], bbox.coord["east"])
    map_width = lat_lon_to_distance(bbox.coord["north"], bbox.coord["north"], bbox.coord["west"], bbox.coord["east"])
    print("Map size: ", map_width, "x", map_height)

    shutil.rmtree(WORK_PATH)
    os.makedirs(WORK_PATH, exist_ok=True)

    with open(otc_file_name, "w") as otc_file:
        otc_file.write("Pages_X=0 \n\
Pages_Y=0 \n\
Flat=1 \n\
WorldSizeX=" + str(int(map_height)) + "\n\
WorldSizeZ=" + str(int(map_width)) + "\n\
WorldSizeY=0\n\
PageFileFormat=" + MAP_NAME + "-page-0-0.otc" + "\n\
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

    with open(terrn2_file_name, "w") as terrn2_file:
        terrn2_file.write("[General]\n\
Name = mapgen terrain\n\
GeometryConfig = " + MAP_NAME + ".otc" + "\n\
Water = 0\n\
AmbientColor = 1, 1, 1\n\
StartPosition = " + str(int(map_width / 2)) + " 0 " + str(int(map_height / 2)) + "\n\
SandStormCubeMap = tracks/skyboxcol\n\
Gravity = -9.81\n\
CategoryID = 129\n\
Version = 1\n\
GUID = 0\n\
[Authors]\n\
terrain = mapgen\n\
[Objects]\n" + MAP_NAME + ".tobj=\n")

    with open(page_otc_file_name, "w") as page_otc_file:
        page_otc_file.write(
            MAP_NAME + ".png\n1\n4    , asphalt_diffusespecular.dds      ,    asphalt_normalheight.dds\n")

    with open(tobj_file_name, "w") as tobj_file:
        tobj_file.write("\n")


def create_base():
    with ZipFile(EXPORT_PATH + MAP_NAME + ".zip", 'w') as zip_object:
        zip_object.write(otc_file_name, arcname=MAP_NAME + ".otc")
        zip_object.write(page_otc_file_name, arcname=MAP_NAME + "-page-0-0.otc")
        zip_object.write(terrn2_file_name, arcname=MAP_NAME + ".terrn2")
        zip_object.write(RESOURCE_PATH + "asphalt_diffusespecular.dds",
                         arcname="asphalt_diffusespecular.dds")
        zip_object.write(RESOURCE_PATH + "asphalt_normalheight.dds", arcname="asphalt_normalheight.dds")
        zip_object.write(RESOURCE_PATH + "mapgen.material", arcname="mapgen.material")
        zip_object.write(RESOURCE_PATH + "grass.png", arcname="grass.png")
        zip_object.write(RESOURCE_PATH + "grass_dandelion.png", arcname="grass_dandelion.png")


def add_file(file_name_to_add):
    with ZipFile(EXPORT_PATH + MAP_NAME + ".zip", 'a') as zip_object:
        zip_object.write(gvar.WORK_PATH + file_name_to_add, arcname=file_name_to_add)
