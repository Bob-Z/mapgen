import config


def create_file():
    with open(config.data["work_path"] + config.data["map_name"] + "-page-0-0.otc", "w") as page_otc_file:
        page_otc_file.write(
            config.data["map_name"] + "_height.png\n" + "\
6\n\
; worldSize, diffusespecular, normalheight, blendmap, blendmapmode, alpha\n\
6, dirt_diffusespecular.dds, dirt_normalheight.dds\n \
1, asphalt_diffusespecular.dds, asphalt_normalheight.dds, surface0.png, R, 0.9\n\
6, rock_diffusespecular.dds, rock_normalheight.dds, surface0.png, G, 0.9\n\
5, sand_diffusespecular.dds, sand_normalheight.dds, surface0.png, B, 0.9\n\
4, grass_diffusespecular.dds, grass_normalheight.dds, surface1.png, R, 0.8\n\
3.3, gravel_diffusespecular.dds, gravel_normalheight.dds, surface1.png, G, 0.8\n")
