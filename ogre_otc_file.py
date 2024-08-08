import config
import gvar
import topography


def get_height():
    if topography.is_enabled():
        return topography.get_total_height()
    else:
        return config.data["ground_line"]  # just managing water depth for now


def create_file():
    with open(config.data["work_path"] + config.data["map_name"] + ".otc", "w") as otc_file:
        otc_file.write("\
PagesX=0\n\
PagesZ=0\n\
PageSize=" + str(int(gvar.map_size / gvar.map_precision) + 1) + "\n\
Flat=0 \n\
WorldSizeX=" + str(int(gvar.map_size)) + "\n\
WorldSizeZ=" + str(int(gvar.map_size)) + "\n\
WorldSizeY=" + str(int(get_height())) + "\n\
PageFileFormat=" + config.data["map_name"] + "-page-{X}-{Z}.otc" + "\n\
LayerBlendMapSize=1024\n\
disableCaching=1\n\
MaxPixelError=5\n\
minBatchSize=33\n\
maxBatchSize=65\n\
LightmapEnabled=0\n\
NormalMappingEnabled=0\n\
SpecularMappingEnabled=0\n\
ParallaxMappingEnabled=0\n\
GlobalColourMapEnabled=0\n\
ReceiveDynamicShadowsDepth=0\n\
CompositeMapDistance=4000\n\
CompositeMapSize=1024\n\
LightMapSize=1024\n\
SkirtSize=30\n\
DebugBlendMaps=1\n")
