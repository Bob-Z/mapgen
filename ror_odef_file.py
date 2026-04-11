import ror_zip_file
import config


def create_file(name, collision=True, size_x=1, size_y=1, size_z=1):
    with open(config.data["work_path"] + name + ".odef", "w") as odef_file:
        odef_file.write(name + ".mesh\n" \
                        + str(size_x) + "," \
                        + str(size_y) + ","\
                        + str(size_z) + "\n")

        if collision is True:
            odef_file.write("beginmesh\n\
mesh " + name + ".mesh\n\
endmesh\n")

        odef_file.write("end\n")

    ror_zip_file.add_to_zip_file_list(name + ".odef")
