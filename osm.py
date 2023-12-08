import overpy
from gvar import LOG_PATH
import sys
import bbox
import time


def get_data():
    bounding_box = str(bbox.coord["south"]) + "," + str(bbox.coord["west"]) + "," + str(
        bbox.coord["north"]) + "," + str(bbox.coord["east"])

    print("Requesting OpenStreetMap")
    start_time = time.time()
    overpy_api = overpy.Overpass()
    result = overpy_api.query(
        "(>>;node(" + bounding_box + ");>>;way(" + bounding_box + ");>>;rel(" + bounding_box + "););out;")
    end_time = time.time()

    print("Done in " + str(end_time - start_time) + " seconds")
    print("")

    dump_result_to_file(result)

    return result


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
