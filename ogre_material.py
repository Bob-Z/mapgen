import config
import ror_zip_file
import PIL

texture_qty = 0
material_str = ""


def create_material_hedge(dest_width, dest_length):
    return create_material(config.data["hedge_tex_name"], config.data["hedge_tex_width"],
                           config.data["hedge_tex_height"],
                           dest_width, dest_length)


# return material name
def create_material(tex_name, tex_width, tex_length, dest_width, dest_length):
    global texture_qty
    global material_str

    if dest_width == 0.0 or dest_length == 0.0:
        print("Warning create_material invalid destination dimension: width=", dest_width, ",length=", dest_length)
        return config.data["wall_texture"]
    name = "mapgen_generated_" + str(texture_qty)
    material_str += "material " + name + "\n"
    material_str += "{\n"
    material_str += "   technique\n"
    material_str += "   {\n"
    material_str += "       pass\n"
    material_str += "       {\n"
    material_str += "           texture_unit\n"
    material_str += "           {\n"
    material_str += "               texture " + tex_name + "\n"
    material_str += "               scale " + str(tex_width / dest_width) + " " + str(tex_length / dest_length) + "\n"
    material_str += "           }\n"
    material_str += "       }\n"
    material_str += "   }\n"
    material_str += "}\n"
    material_str += "\n"

    texture_qty += 1

    return name


def create_material_color(colour):
    global material_str

    # OSM documented color
    if colour == "brown":
        colour = "#804000"
    elif colour == "red":
        colour = "#FF0000"
    elif colour == "yellow":
        colour = "#FFFF00"
    elif colour == "gray":
        colour = "#808080"
    elif colour == "green":
        colour = "#008000"
    elif colour == "white":
        colour = "#FFFFFF"
    elif colour == "black":
        colour = "#000000"
    elif colour == "blue":
        colour = "#0000FF"
    elif colour == "orange":
        colour = "#FF8000 "

    name = "colour_" + colour

    if material_str.find(name) != -1:
        return name

    # Create texture file
    try:
        tex = PIL.Image.new(mode="RGB", size=(1, 1), color=colour)
    except ValueError:
        print("Unsupported colour:", colour)
        return None
    tex.save(config.data["work_path"] + name + ".png", "PNG")
    ror_zip_file.add_to_zip_file_list(name + ".png")

    # Add to material file
    material_str += "material " + name + " : RoR/Managed_Mats/Base\n"
    material_str += "{\n"
    material_str += "   technique BaseTechnique\n"
    material_str += "   {\n"
    material_str += "       pass BaseRender\n"
    material_str += "       {\n"
    material_str += "           cull_hardware none\n"
    material_str += "           cull_software none\n"
    material_str += "           texture_unit Diffuse_Map\n"
    material_str += "           {\n"
    material_str += "               texture " + name + ".png\n"
    material_str += "           }\n"
    material_str += "       }\n"
    material_str += "   }\n"
    material_str += "}\n"
    material_str += "\n"

    return name


def create_file():
    global material_str

    with open(config.data["work_path"] + "magen_generated.material", "w") as material_file:
        material_file.write(material_str)

    ror_zip_file.add_to_zip_file_list("magen_generated.material")
