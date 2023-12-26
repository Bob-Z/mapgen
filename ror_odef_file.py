import ror_zip_file
import config


def create_file(new_object):
    with open(config.config["work_path"] + new_object["name"] + ".odef", "w") as odef_file:
        odef_file.write(new_object["name"] + ".mesh\n \
1, 1, 1\n")

        if new_object["collision"] is True:
            odef_file.write("beginmesh\n\
mesh " + new_object["name"] + ".mesh\n\
endmesh\n")

        odef_file.write("end\n")

    ror_zip_file.add_file(new_object["name"] + ".odef")
