import ror_zip_file
from gvar import MAP_NAME
from gvar import WORK_PATH
from gvar import TERRN2_FILE_NAME


def create_file(map_width, map_height):

    with open(WORK_PATH + TERRN2_FILE_NAME, "w") as terrn2_file:
        terrn2_file.write("[General]\n\
    Name = mapgen terrain\n\
    GeometryConfig = " + MAP_NAME + ".otc" + "\n\
    CaelumConfigFile = " + MAP_NAME + ".os" + "\n\
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

