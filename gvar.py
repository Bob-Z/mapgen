import os

import config

EXPORT_PATH = os.getenv("HOME") + "/.rigsofrods/mods/"

is_water_map = False

GROUND_LEVEL = 0.0


def set_is_water_map(is_water):
    global is_water_map
    global GROUND_LEVEL
    if is_water is True:
        is_water_map = True
        GROUND_LEVEL = config.data["water_line"] + config.data["ground_above_water"]
