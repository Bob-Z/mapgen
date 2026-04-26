import config
import ror_zip_file
import PIL

material_str = ""


def create_material_color(tags):
    global material_str

    colour = None
    if "colour" in tags:
        colour = tags["colour"]
        tags.pop("colour")
    if "building:colour" in tags:
        colour = tags["building:colour"]
        tags.pop("building:colour")
    if "roof:colour" in tags:
        colour = tags["roof:colour"]
        tags.pop("roof:colour")

    if colour is None:
        return None

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
