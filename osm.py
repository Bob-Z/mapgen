import overpy
import osm_node
import osm_way
from gvar import LOG_PATH
import sys
import bbox
import ror_zip_file
import gvar


def add_data_to_output_file():
    bounding_box = str(bbox.coord["north"]) + "," + str(bbox.coord["west"]) + "," + str(bbox.coord["south"]) + "," + str(bbox.coord["east"])

    overpy_api = overpy.Overpass()
    result = overpy_api.query(
        "node(" + bounding_box + ");out;way(" + bounding_box + ");out;rel(" + bounding_box + ");out;")

    print("Request to OpenStreetMap done")
    print("")

    dump_result_to_file(result)

    osm_node.process(result)
    osm_way.process(result)
    process_relation(result)

    ror_zip_file.add_file(gvar.MAP_NAME + ".tobj")


def dump_result_to_file(result):
    original_stdout = sys.stdout

    with open(LOG_PATH + "osm_request.txt", "w") as result_file:
        sys.stdout = result_file

        for node in result.nodes:
            print(node, node.tags)

        for way in result.ways:
            print(way, way.tags)

        for relation in result.relations:
            print(relation, relation.tags)

    sys.stdout = original_stdout


def process_node(result):
    for node in result.nodes:
        if "building" in node.tags and node.tags["building"] == "yes":
            print("node", node, " : ", node.tags)


def process_relation(result):
    for relation in result.relations:
        if "building" in relation.tags and relation.tags["building"] == "yes":
            print("relation", relation, " : ", relation.tags)
