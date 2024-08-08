import ror_tobj_file
import random
import helper
from wikidata.client import Client
import topography

wikidata_client = Client()


def process(node):
    if "natural" in node.tags:
        if node.tags["natural"] == "tree":
            ror_tobj_file.add_object(x=helper.lon_to_x(node.lon), y=helper.lat_to_y(node.lat),
                                     z=topography.get_z(node.lon, node.lat), rx=90.0,
                                     ry=float(random.randint(0, 359)), rz=0.0, name="tree1")
            node.tags.pop("natural")

    if "amenity" in node.tags:
        if node.tags["amenity"] == "bench":
            # FIXME remove this + 0.5
            ror_tobj_file.add_object(x=helper.lon_to_x(node.lon), y=helper.lat_to_y(node.lat),
                                     z=topography.get_z(node.lon, node.lat) + 0.5, rx=0.0,
                                     ry=0.0, rz=float(random.randint(0, 359)), name="bench")
            node.tags.pop("amenity")
