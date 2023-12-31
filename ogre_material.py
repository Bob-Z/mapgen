import config
import ror_zip_file

texture_qty = 0
material_str = ""


def create_material_swimming_pool(dest_width, dest_length):
    return create_material(config.data["swimming_pool_tex_name"], config.data["swimming_pool_tex_width"],
                           config.data["swimming_pool_tex_height"],
                           dest_width, dest_length)


# return material name
def create_material(tex_name, tex_width, tex_length, dest_width, dest_length):
    global texture_qty
    global material_str

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


def add_file():
    global material_str

    with open(config.data["work_path"] + "magen_generated.material", "w") as material_file:
        material_file.write(material_str)

    ror_zip_file.add_file("magen_generated.material")
