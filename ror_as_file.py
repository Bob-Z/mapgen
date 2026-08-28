import config
import ror_as_script
import ror_zip_file
import ror_terrn2_file


def write():
    script_name = config.data["map_name"] + ".terrn.as"

    road_bots_string = ror_as_script.generate_road_bots()

    if road_bots_string is not None and road_bots_string != "":
        with open(config.data["work_path"] + script_name, "a") as as_file:
            as_file.write(road_bots_string)

        ror_terrn2_file.add_as_script()
        ror_zip_file.add_to_zip_file_list(script_name)
