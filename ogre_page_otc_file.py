import config


def create_file():
    world_ground = "4, dirt_diffusespecular.dds, dirt_normalheight.dds\\n"
    if config.data["world_ground"] == "dirt":
        print("World ground: dirt")
    elif config.data["world_ground"] == "snow":
        world_ground = "10, snow_diffusespecular.dds, snow_normalheight.dds\\n"
        print("World ground: snow")
    elif config.data["world_ground"] == "red_dirt":
        world_ground = "10, red_dirt_diffusespecular.dds, red_dirt_normalheight.dds\\n"
        print("World ground: red dirt")
    else:
        print("Unknown world ground", config.data["world_ground"], "defaulting to dirt")

    with open(config.data["work_path"] + config.data["map_name"] + "-page-0-0.otc", "w") as page_otc_file:
        page_otc_file.write(
            config.data["map_name"] + "_height.png\n" + "\
6\n\
; worldSize, diffusespecular, normalheight, blendmap, blendmapmode, alpha\n"
            + world_ground +
            "4, dirt_diffusespecular.dds, dirt_normalheight.dds\n\
            1, asphalt_diffusespecular.dds, asphalt_normalheight.dds, surface0.png, R, 0.9\n\
            6, rock_diffusespecular.dds, rock_normalheight.dds, surface1.png, R, 0.9\n\
            5, sand_diffusespecular.dds, sand_normalheight.dds, surface2.png, R, 0.9\n\
            4, grass_diffusespecular.dds, grass_normalheight.dds, surface3.png, R, 0.9\n\
            3, gravel_diffusespecular.dds, gravel_normalheight.dds, surface4.png, R, 0.9\n")
