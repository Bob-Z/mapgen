import gvar
import ror_zip_file


def create_file(new_object):
    with open(gvar.WORK_PATH + new_object["name"] + ".odef", "w") as odef_file:
        odef_file.write(new_object["name"] + ".mesh\n \
1, 1, 1\n")

        if new_object["collision"] is True:
            odef_file.write("beginmesh\n\
mesh " + new_object["name"] + ".mesh\n\
endmesh\n")

        odef_file.write("end\n")

    ror_zip_file.add_file(new_object["name"] + ".odef")
