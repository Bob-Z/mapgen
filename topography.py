from bmi_topography import Topography
import bbox
import helper
import ogre_map_height
import config
#import matplotlib.pyplot as plt

topo = None
enabled = False
elevation_min = None
elevation_max = None


def is_enabled():
    global enabled
    return enabled


def get(api_key):
    if api_key is not None:
        print("Fetch topography, please wait\n")

        params = Topography.DEFAULT.copy()
        params["south"] = bbox.coord["south"]
        params["north"] = bbox.coord["north"]
        params["west"] = bbox.coord["west"]
        params["east"] = bbox.coord["east"]
        params["api_key"] = api_key
        params["dem_type"] = "COP30"
        # ('SRTMGL3', 'SRTMGL1', 'SRTMGL1_E', 'AW3D30', 'AW3D30_E', 'SRTM15Plus', 'NASADEM', 'COP30', 'COP90')

        global topo
        topo = Topography(**params)
        topo.fetch()
        topo.load()

        global elevation_min
        global elevation_max
        elevation_min = topo.da.data.min()
        elevation_max = topo.da.data.max()

        global enabled
        enabled = True

        #topo.da.plot()
        #plt.show()

    else:
        print("No OpenTopography API key provided, using flat map")


def fill_map_height(draw):
    print("Generating height from topography, please wait\n")

    image_width = draw.im.size[0]
    image_height = draw.im.size[1]

    for w in range(image_width):
        # longitude = bbox.coord["west"] + (((bbox.coord["east"] - bbox.coord["west"]) / width) * w)
        width_percent = w / image_width
        for h in range(image_height):
            # latitude = bbox.coord["south"] + (((bbox.coord["north"] - bbox.coord["south"]) / height) * h)
            height_percent = h / image_height

            elevation = get_elevation_percent(width_percent, height_percent)

            color = elevation * ogre_map_height.MAX_COLOR

            draw.point((w, h), fill=int(color))


def get_total_height():
    global elevation_min
    global elevation_max

    return elevation_max - elevation_min


# input are percentage of width and height on the topography data
def get_elevation_percent(width_percent, height_percent):
    topo_data_index_w = topo.da.data.shape[2] * width_percent
    topo_data_index_h = topo.da.data.shape[1] * height_percent

    # Try to smooth topology data
    topo_w_next = int(topo_data_index_w) + 1
    topo_h_next = int(topo_data_index_h) + 1
    # FIXME better handling for last data ?
    if topo_w_next >= topo.da.data.shape[2]:
        topo_w_next = topo.da.data.shape[2] - 1
    if topo_h_next >= topo.da.data.shape[1]:
        topo_h_next = topo.da.data.shape[1] - 1

    elevation_1_1 = topo.da.data[0][int(topo_data_index_h)][int(topo_data_index_w)]
    elevation_2_1 = topo.da.data[0][int(topo_h_next)][int(topo_data_index_w)]
    elevation_1_2 = topo.da.data[0][int(topo_data_index_h)][int(topo_w_next)]
    elevation_2_2 = topo.da.data[0][int(topo_h_next)][int(topo_w_next)]

    elevation_h_1 = elevation_1_1 + ((elevation_2_1 - elevation_1_1) * (topo_data_index_h % 1))
    elevation_h_2 = elevation_1_2 + ((elevation_2_2 - elevation_1_2) * (topo_data_index_h % 1))

    elevation = elevation_h_1 + ((elevation_h_2 - elevation_h_1) * (topo_data_index_w % 1))

    return (elevation - elevation_min) / get_total_height()


def get_elevation_from_lon_lat(lon, lat):
    if helper.is_inside_lon_lat(lon, lat):
        width_percent = (float(lon) - bbox.coord["west"]) / (bbox.coord["east"] - bbox.coord["west"])
        height_percent = (float(lat) - bbox.coord["north"]) / (bbox.coord["south"] - bbox.coord["north"])

        return get_elevation_percent(width_percent, height_percent) * get_total_height()
    else:
        return config.data["ground_line"]


def get_z(lon, lat):
    if is_enabled():
        z = get_elevation_from_lon_lat(lon, lat)
    else:
        z = config.data["ground_line"]

    return z
