import requests
import gvar
import bbox
import os
import config
import pickle
import time


def get_data():
    bounding_box = str(bbox.coord["south"]) + "," + str(bbox.coord["west"]) + "," + str(
        bbox.coord["north"]) + "," + str(bbox.coord["east"])

    cache_file_path = config.data["cache_path"] + "/" + bounding_box + ".elevation"
    if os.path.isfile(cache_file_path):
        print("Reading OpenElevation cache file\n")
        with open(cache_file_path, 'rb') as file:
            result = pickle.load(file)
    else:
        print("Requesting OpenElevation")
        start_time = time.time()

        all_coord = []
        all_respond = []

        lon_quantum = (bbox.coord["east"] - bbox.coord["west"]) / gvar.map_size
        lat_quantum = (bbox.coord["south"] - bbox.coord["north"]) / gvar.map_size

        coord_qty = 0
        for x in range(int(gvar.map_size)):
            for y in range(int(gvar.map_size)):
                lon = bbox.coord["west"] + (x * lon_quantum)
                lat = bbox.coord["north"] + (y * lat_quantum)
                all_coord.append({"latitude": lat, "longitude": lon})

                coord_qty += 1
                if coord_qty % 1000 == 0:
                    json = {"locations": all_coord}
                    url = 'https://api.open-elevation.com/api/v1/lookup'
                    respond = requests.post(url, json=json)

                    if respond.status_code != 200:
                        print("Failed with error:", respond.status_code)
                        return
                    all_respond.append(respond.json())
                    all_coord = []

        json = {"locations": all_coord}
        url = 'https://api.open-elevation.com/api/v1/lookup'
        respond = requests.post(url, json=json)

        if respond.status_code != 200:
            print("Failed")
            return
        all_respond.append(respond.json())

        end_time = time.time()

        print("Done in " + str(end_time - start_time) + " seconds\n")

        print("Writing OpenElevation cache file\n")
        with open(cache_file_path, 'wb') as file:
            pickle.dump(all_respond, file)

        print(all_respond)

