import ror_tobj_file
import random
import helper
from wikidata.client import Client


wikidata_client = Client()

def process(node):
    if "wikidata" in node.tags:
        wiki = wikidata_client.get(node.tags["wikidata"], load=False)
        if "P4896" in wiki.attributes["claims"]:
            name = wiki.attributes["claims"]["P4896"][0]["mainsnak"]["datavalue"]["value"]
            #pyWikiCommons.download_commons_image(name, config.data["work_path"])
            print("---", name)

    if "natural" in node.tags:
        if node.tags["natural"] == "tree":
            ror_tobj_file.add_object(x=helper.lon_to_x(node.lon), y=helper.lat_to_y(node.lat), z=0.0, rx=90.0,
                                     ry=float(random.randint(0, 359)), rz=0.0, name="tree1")
            node.tags.pop("natural")

    if "amenity" in node.tags:
        if node.tags["amenity"] == "bench":
            ror_tobj_file.add_object(x=helper.lon_to_x(node.lon), y=helper.lat_to_y(node.lat), z=0.5, rx=0.0,
                                     ry=0.0, rz=float(random.randint(0, 359)), name="bench")
            node.tags.pop("amenity")
