import config
import sys
from PIL import Image

# Return a Pillow image
def load_texture(filename):
    try:
        return Image.open(config.data["cache_path"] + "/" + filename + ".png")
    except Exception:
        return None

def save_texture(pillow_image, filename):
    pillow_image.save(config.data["cache_path"] + "/" + filename + ".png", "PNG")
