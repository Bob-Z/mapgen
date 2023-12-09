import os

MAP_NAME = "mapgen"
WORK_PATH = "./work/"
LOG_PATH = "./log/"
RESOURCE_PATH = "./resource/"
TERRN2_FILE_NAME = MAP_NAME + ".terrn2"
print("Work path:", WORK_PATH)
EXPORT_PATH = os.getenv("HOME") + "/.rigsofrods/mods/"
print("Export path: ", EXPORT_PATH)

is_water_map = False
WATER_LINE = 5.0
GROUND_ABOVE_WATER = 1.0  # This value is high to avoid (most) glitches with Hydrax waves.

GROUND_LEVEL = 0.0
if is_water_map is True:
    GROUND_LEVEL = WATER_LINE + GROUND_ABOVE_WATER
