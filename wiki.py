import config
from wikidata.client import Client
from pyWikiCommons import pyWikiCommons
import os
import shutil
import subprocess
import ror_odef_file
import ror_tobj_file
import ror_zip_file
import osm

wikidata_client = Client()


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


# Return True if got successfully
def get_data(entity, osm_data=None):
    if config.data["use_wikidata"] is False:
        return False

    found = False

    if "wikidata" in entity.tags:
        wiki = wikidata_client.get(entity.tags["wikidata"], load=True)
        if "P4896" in wiki.attributes["claims"]:
            wiki_name = wiki.attributes["claims"]["P4896"][0]["mainsnak"]["datavalue"]["value"]

            name = wiki_name.replace(' ', '_')
            cache_stl_file_path = config.data["cache_path"] + name
            work_stl_file_path = config.data["work_path"] + name
            if os.path.isfile(cache_stl_file_path):
                print("Reading cached 3D model file " + cache_stl_file_path + " \n")
                shutil.copyfile(cache_stl_file_path, work_stl_file_path)
            else:
                pyWikiCommons.download_commons_image(wiki_name, config.data["work_path"])
                shutil.move(config.data["work_path"] + "/File:" + wiki_name, config.data["work_path"] + name)
                shutil.copyfile(work_stl_file_path, cache_stl_file_path)
                print("P4896 available for entity", entity, name)

            subprocess.Popen([config.data["OgreAssimp_path"] + "OgreAssimpConverter", work_stl_file_path],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.STDOUT
                             )

            short_name = name.removesuffix(".stl")
            ror_zip_file.add_to_zip_file_list(short_name + ".mesh")
            ror_zip_file.add_to_zip_file_list(short_name + ".material")
            ror_odef_file.create_file(short_name)
            ror_tobj_file.add_object(0, 0, 0, 0, 0, 0, short_name)
            config.data["use_wikidata"] = False
            found = True

    if found is False and osm_data is not None:
        for member in entity.members:
            way = osm.get_way_by_id(osm_data, member.ref)
            if way is not None:
                if get_data(way) is True:
                    found = True
                    break

    # Remove all ways of the relation
    if found is True and osm_data is not None:
        for member in entity.members:
            index = 0
            while index < len(osm_data.ways):
                if osm_data.ways[index].id == member.ref:
                    osm_data.way_ids.pop(index)
                    osm_data.ways.pop(index)
                    print("remove", osm_data.ways[index])
                    break
                index += 1

    return found
