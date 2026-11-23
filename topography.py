from bmi_topography import Topography
import bbox
import helper
import config
import numpy as np
from PIL import Image

# import matplotlib.pyplot as plt

topo = None
enabled = False
topo_img = None


def is_enabled():
    global enabled
    return enabled


def get(api_key):
    if api_key is not None and api_key != "":
        print("Fetch topography, please wait\n")

        params = Topography.DEFAULT.copy()
        params["south"] = bbox.coord["south"]
        params["north"] = bbox.coord["north"]
        params["west"] = bbox.coord["west"]
        params["east"] = bbox.coord["east"]
        params["api_key"] = api_key
        params["dem_type"] = config.data["topography_dataset"]
        # ('SRTMGL3', 'SRTMGL1', 'SRTMGL1_E', 'AW3D30', 'AW3D30_E', 'SRTM15Plus', 'NASADEM', 'COP30', 'COP90')

        global topo
        topo = Topography(**params)
        topo.fetch()
        topo.load()

        global enabled
        enabled = True

        # topo.da.plot()
        # plt.show()

    else:
        print("No OpenTopography API key provided, using flat map\n")


def fill_map_height(size, max_color):
    print("Generating height from topography\n")

    elevation = topo.da.squeeze().to_numpy()

    # Replace NaNs (e.g., ocean/missing data) with minimum elevation if needed
    elevation = np.nan_to_num(elevation, nan=np.nanmin(elevation))

    # Normalize to 0..max_color and cast to uint16
    elev_min, elev_max = elevation.min(), elevation.max()
    gray_16bit = (
            (elevation - elev_min) / (elev_max - elev_min) * max_color
    ).astype(np.uint16)

    img = Image.fromarray(gray_16bit)
    img.save("heightmap_16bit.png")

    global topo_img
    topo_img = img.resize(size, resample=Image.BICUBIC)
    return topo_img


def get_total_elevation():
    global topo
    return topo.da.data.max() - topo.da.data.min()


def get_topo_elevation():
    global topo
    return topo.da.data.max() - topo.da.data.min()


# input are percentage of width and height on the topography data
def get_elevation_percent(width_percent, height_percent):
    global topo_img
    return topo_img.getpixel((topo_img.width * width_percent, topo_img.height * height_percent)) / 65535


def get_elevation_from_lon_lat(lon, lat):
    if helper.is_inside_lon_lat(lon, lat):
        width_percent = (float(lon) - bbox.coord["west"]) / (bbox.coord["east"] - bbox.coord["west"])
        height_percent = (float(lat) - bbox.coord["north"]) / (bbox.coord["south"] - bbox.coord["north"])

        return get_elevation_percent(width_percent, height_percent) * get_total_elevation()
    else:
        return config.data["ground_line"]


def get_z(lon, lat):
    if is_enabled():
        z = get_elevation_from_lon_lat(lon, lat)
    else:
        z = config.data["ground_line"]

    return z
