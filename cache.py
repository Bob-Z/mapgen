import config
import bbox
import os
import pickle
from PIL import Image


# Return a Pillow image
def load_texture(filename):
    try:
        return Image.open(config.data["cache_path"] + "/" + filename + ".png")
    except Exception:
        return None


def save_texture(pillow_image, filename):
    pillow_image.save(config.data["cache_path"] + "/" + filename + ".png", "PNG")


def get_osm_elements_filename():
    return config.data["cache_path"] + "/" + bbox.bounding_box + "," + str(config.data["map_size"])


def load_osm_elements():
    cache_file_path = get_osm_elements_filename()
    if os.path.isfile(cache_file_path):
        print("Reading OpenStreetMap cache file " + cache_file_path + "\n")
        with open(cache_file_path, 'rb') as file:
            elements = pickle.load(file)
            return elements

    return None


def save_osm_elements(elements):
    cache_file_path = get_osm_elements_filename()
    print("Writing OpenStreetMap cache file " + cache_file_path + "\n")
    with open(cache_file_path, 'wb') as file:
        pickle.dump(elements, file)
