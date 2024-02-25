import ror_zip_file
import config


def create_file(name, collision=True):
    with open(config.data["work_path"] + name + ".odef", "w") as odef_file:
        odef_file.write(name + ".mesh\n \
1, 1, 1\n")

        if collision is True:
            odef_file.write("beginmesh\n\
mesh " + name + ".mesh\n\
endmesh\n")

        odef_file.write("end\n")

    ror_zip_file.add_to_zip_file_list(name + ".odef")
