import ror_tobj_file
import random
import helper


def process(osm_data):
    for node in osm_data.nodes:
        if "natural" in node.tags:
            if node.tags["natural"] == "tree":
                ror_tobj_file.add_object(x=helper.lat_to_x(node.lat), y=helper.lon_to_y(node.lon), z=0.5, rx=90.0,
                                         ry=float(random.randint(0, 359)), rz=0.0, name="tree1")
                node.tags.pop("natural")

        if "amenity" in node.tags:
            if node.tags["amenity"] == "bench":
                ror_tobj_file.add_object(x=helper.lat_to_x(node.lat), y=helper.lon_to_y(node.lon), z=0.5, rx=0.0,
                                         ry=0.0, rz=float(random.randint(0, 359)), name="bench")
                node.tags.pop("amenity")
