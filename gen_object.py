import ror_tobj_file
import random
import helper
import topography


def process(feature):
    if "natural" in feature["properties"]["tags"]:
        if feature["properties"]["tags"]["natural"] == "tree":
            lon = feature["geometry"]["coordinates"][0]
            lat = feature["geometry"]["coordinates"][1]
            ror_tobj_file.add_object(x=helper.lon_to_x(lon), y=helper.lat_to_y(lat),
                                     z=topography.get_z(lon, lat), rx=90.0,
                                     ry=float(random.randint(0, 359)), rz=0.0, name="tree1")
            feature["properties"]["tags"].pop("natural")

    if "amenity" in feature["properties"]["tags"]:
        if feature["properties"]["tags"]["amenity"] == "bench":
            lon = feature["geometry"]["coordinates"][0]
            lat = feature["geometry"]["coordinates"][1]

            # FIXME remove this + 0.5
            ror_tobj_file.add_object(x=helper.lon_to_x(lon), y=helper.lat_to_y(lat),
                                     z=topography.get_z(lon, lat) + 0.5, rx=0.0,
                                     ry=0.0, rz=float(random.randint(0, 359)), name="bench")
            feature["properties"]["tags"].pop("amenity")
