import math
import config
from wikidata.client import Client
from pyWikiCommons import pyWikiCommons
import os
import shutil
import subprocess
import topography
import helper
import ror_odef_file
import ror_tobj_file
import ror_zip_file
import osm
import mesh
import urllib
import pickle

# import matplotlib.pyplot as plt

wikidata_client = Client()

wikidata_found = 0
wikidata_downloaded = 0
wikidata_read_from_cache = 0
wikidata_with_3d = 0
wikidata_cleaned_crossing = 0

wikidata_id_found = []

wikidata_3D_model_shape = []


def init():
    if config.data["use_wikidata"] is True:
        try:
            subprocess.Popen([config.data["OgreAssimp_path"] + "OgreAssimpConverter", ],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.STDOUT)
        except:
            print("OgreAssimpConverter not found in " + config.data[
                "work_path"] + ", wikidata's 3D model download disabled")
            config.data["use_wikidata"] = False
        else:
            print("OgreAssimpConverter found, wikidata's 3D model download enabled")


# Return True if successfully got data
def get_data(entity, osm_data=None):
    found = False

    if "wikidata" in entity.tags:
        global wikidata_found
        global wikidata_id_found

        if entity.tags["wikidata"] in wikidata_id_found:
            print(entity.tags["wikidata"], "already found, skipping")
            return False

        wikidata_found += 1
        cache_wikidata_file_path = config.data["cache_path"] + "/wikidata_" + entity.tags["wikidata"]
        if os.path.isfile(cache_wikidata_file_path):
            with open(cache_wikidata_file_path, "rb") as pickle_file:
                wiki = pickle.load(pickle_file)
            global wikidata_read_from_cache
            wikidata_read_from_cache += 1
        else:
            try:
                wiki = wikidata_client.get(entity.tags["wikidata"], load=True)
                with open(cache_wikidata_file_path, "wb") as pickle_file:
                    pickle.dump(wiki, pickle_file)
                    global wikidata_downloaded
                    wikidata_downloaded += 1
            except urllib.error.HTTPError as e:
                print("Cannot download wikidata page ", entity.tags["wikidata"], ":", e,
                      ". Try to update wikidata package.")
                return False

        if "P4896" in wiki.attributes["claims"]:
            wiki_name = wiki.attributes["claims"]["P4896"][0]["mainsnak"]["datavalue"]["value"]

            name = wiki_name.replace(' ', '_')
            cache_stl_file_path = config.data["cache_path"] + "/" + name
            work_stl_file_path = config.data["work_path"] + "/" + name
            if os.path.isfile(cache_stl_file_path):
                print("Reading cached 3D model file " + cache_stl_file_path)
                shutil.copyfile(cache_stl_file_path, work_stl_file_path)
            else:
                print("Download 3D model file " + cache_stl_file_path)
                pyWikiCommons.download_commons_image(wiki_name, config.data["work_path"])
                shutil.move(config.data["work_path"] + "/File:" + wiki_name, config.data["work_path"] + name)
                shutil.copyfile(work_stl_file_path, cache_stl_file_path)

            process = subprocess.Popen([config.data["OgreAssimp_path"] + "OgreAssimpConverter", work_stl_file_path],
                                       stdout=subprocess.DEVNULL,
                                       stderr=subprocess.STDOUT
                                       )
            process.wait()

            short_name = name.removesuffix(".stl")
            ror_zip_file.add_to_zip_file_list(short_name + ".mesh")
            ror_zip_file.add_to_zip_file_list(short_name + ".material")

            # convert bin mesh to XML mesh
            process = subprocess.Popen(["OgreXMLConverter", config.data["work_path"] + short_name + ".mesh"],
                                       stdout=subprocess.DEVNULL,
                                       stderr=subprocess.STDOUT
                                       )
            process.wait()

            xml_file_path = config.data["work_path"] + short_name + ".mesh.xml"
            mesh_height = mesh.get_height(xml_file_path)

            if "P2048" in wiki.attributes["claims"]:
                entity_height_str = wiki.attributes["claims"]["P2048"][0]["mainsnak"]["datavalue"]["value"]["amount"]
                entity_height = float(entity_height_str.replace("+", ""))
            else:
                entity_height = osm.get_height(entity)[0]
                if entity_height is None:
                    print("Unable to find height of ", entity.tags["wikidata"])
                    return False

            factor = entity_height / mesh_height

            ror_odef_file.create_file(short_name, size_x=factor, size_y=factor, size_z=factor)

            nodes = None
            if hasattr(entity, "nodes"):
                nodes = entity.nodes
            else:
                for member in entity.members:
                    way = osm.get_way_by_id(osm_data, member.ref)
                    if way is not None:
                        nodes = way.nodes

            if nodes is None:
                print("Can't find nodes for ", entity.tags["wikidata"])
                return False

            lon, lat = osm.get_pseudo_center_lon_lat(nodes)
            rotation = calculate_rotation_angle(nodes, xml_file_path)

            ror_tobj_file.add_object(x=helper.lon_to_x(lon), y=helper.lat_to_y(lat), z=topography.get_z(lon, lat), rx=0,
                                     ry=0,
                                     rz=rotation, name=short_name)

            if config.data["ignore_osm_data_crossing_wikidata_model"] is True:
                wikidata_3D_model_shape.append(helper.node_to_polygon(nodes))

            wikidata_id_found.append(entity.tags["wikidata"])
            global wikidata_with_3d
            wikidata_with_3d += 1
            found = True

    # If entity is a relation, try to find wikidata in each ways
    if found is False and osm_data is not None:
        if hasattr(entity, 'members'):
            for member in entity.members:
                way = osm.get_way_by_id(osm_data, member.ref)
                if way is not None:
                    if get_data(way) is True:
                        found = True
                        break

    return found


# this give an angle between the largest edge of the given way and the largest edge of the given mesh
# This is highly empirical, but it seems to work
def calculate_rotation_angle(nodes, xml_file_path):
    entity_xy = osm.get_extreme_x_y(nodes)
    mesh_xy = mesh.get_extreme_x_y(xml_file_path)

    # get longest entity segment
    entity_max_size = 0
    entity_max_size_index = 0
    entity_segment_size = [0, 0, 0, 0]
    mesh_max_size = 0
    mesh_max_size_index = 0
    mesh_segment_size = [0, 0, 0, 0]
    for i in range(4):
        entity_segment_size[i] = math.sqrt(
            (entity_xy[i][0] - entity_xy[(i + 1) % 4][0]) * (entity_xy[i][0] - entity_xy[(i + 1) % 4][0])
            + (entity_xy[i][1] - entity_xy[(i + 1) % 4][1]) * (entity_xy[i][1] - entity_xy[(i + 1) % 4][1]))
        if entity_segment_size[i] > entity_max_size:
            entity_max_size = entity_segment_size[i]
            entity_max_size_index = i

        mesh_segment_size[i] = math.sqrt(
            (mesh_xy[i][0] - mesh_xy[(i + 1) % 4][0]) * (mesh_xy[i][0] - mesh_xy[(i + 1) % 4][0])
            + (mesh_xy[i][1] - mesh_xy[(i + 1) % 4][1]) * (mesh_xy[i][1] - mesh_xy[(i + 1) % 4][1]))
        if mesh_segment_size[i] > mesh_max_size:
            mesh_max_size = mesh_segment_size[i]
            mesh_max_size_index = i

    entity_v1 = (entity_xy[entity_max_size_index])
    entity_v2 = (entity_xy[(entity_max_size_index - 1) % 4])
    moved_mesh_v1 = (mesh_xy[(mesh_max_size_index - 1) % 4][0] + (entity_v2[0] - mesh_xy[mesh_max_size_index][0]),
                     mesh_xy[(mesh_max_size_index - 1) % 4][1] + (entity_v2[1] - mesh_xy[mesh_max_size_index][1]))

    return helper.angle_between(entity_v1, entity_v2, moved_mesh_v1)


def is_object_crossing(nodes):
    if config.data["use_wikidata"] is True and config.data["ignore_osm_data_crossing_wikidata_model"] is True:
        polygon = helper.node_to_polygon(nodes)
        for shape in wikidata_3D_model_shape:
            if shape.disjoint(polygon) is False:
                global wikidata_cleaned_crossing
                wikidata_cleaned_crossing += 1
                return True
        # x, y = polygon.exterior.xy
        # plt.plot(x, y)
        # x, y = wikidata_3D_model_shape[0].exterior.xy
        # plt.plot(x, y)

        # plt.show(block=True)

    return False


def print_data():
    if config.data["use_wikidata"] is True:
        global wikidata_found
        global wikidata_downloaded
        global wikidata_read_from_cache
        global wikidata_with_3d
        global wikidata_cleaned_crossing

        print("wikidata tags found:", wikidata_found)
        print("wikidata data downloaded:", wikidata_downloaded)
        print("wikidata data read from cache:", wikidata_read_from_cache)
        print("wikidata data with 3D model:", wikidata_with_3d)
        print("OSM objects crossing 3D model ignored:", wikidata_cleaned_crossing)
        print("")
