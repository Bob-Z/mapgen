import config
import ogre_map_height
import gvar

MAX_HEIGHT = config.data["ground_line"]  # just managing water depth for now


def create_file():
    with open(config.data["work_path"] + config.data["map_name"] + ".otc", "w") as otc_file:
        otc_file.write("\
Pages_X=0 \n\
Pages_Y=0 \n\
PageSize=" + str(int(gvar.map_size) * ogre_map_height.MAP_HEIGHT_SIZE_FACTOR + 1) + "\n\
#Flat=1 \n\
Flat=0 \n\
WorldSizeX=" + str(int(gvar.map_size)) + "\n\
WorldSizeZ=" + str(int(gvar.map_size)) + "\n\
WorldSizeY=" + str(int(MAX_HEIGHT)) + "\n\
PageFileFormat=" + config.data["map_name"] + "-page-0-0.otc" + "\n\
LayerBlendMapSize=2048\n\
disableCaching=1\n\
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
