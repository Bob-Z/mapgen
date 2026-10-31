import config
import ror_zip_file
import PIL
import webcolors

if config.data["generate_ai_texture"]:
    import torch
    from diffusers import DiffusionPipeline

    try:
        pipe = DiffusionPipeline.from_pretrained("dream-textures/texture-diffusion", dtype=torch.bfloat16,
                                                 device_map="cuda")
        print()
        print("Using GPU to generate texture")
        print()
    except torch.OutOfMemoryError:
        print()
        print("Not enough GPU RAM. Texture generation disabled.")
        print()
        config.data["generate_ai_texture"] = False

material_str = ""

texture_qty_by_material = {}


def create_material(base, tags):
    if config.data["generate_ai_texture"] is False:
        return create_material_color(tags)

    return create_ai_texture(generate_prompt(base, tags))


def generate_prompt(default_material, tags):
    material = default_material

    if "building:material" in tags:
        material = tags["building:material"]

    if "colour" in tags:
        if tags["colour"][0] != '#':  # ignore RGB colors
            material = tags["colour"] + " " + material
    if "building:colour" in tags:
        if tags["building:colour"][0] != '#':  # ignore RGB colors
            material = tags["building:colour"] + " " + material

    return material


def create_material_color(tags):
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

    colour = colour.replace("_", " ")

    try:
        colour = webcolors.name_to_hex(colour.lower())
    except ValueError:
        pass

    if colour.find("#") == -1:
        colour = "#" + colour

    name = "colour_" + colour

    if material_str.find(name) != -1:
        return name

    # Create texture file
    tex = None
    try:
        tex = PIL.Image.new(mode="RGB", size=(1, 1), color=colour)
    except ValueError:
        print("Unsupported colour:", colour[1:])
        return None

    save_texture(tex, name)

    return name


def create_ai_texture(prompt):
    file_name = prompt.replace(" ", "_")
    file_name = "texture_" + file_name

    texture_qty = 0
    if prompt in texture_qty_by_material:
        texture_qty = texture_qty_by_material[prompt]

    file_name = file_name + "_" + str(texture_qty % config.data["max_texture_by_material"])

    texture_qty += 1
    texture_qty_by_material[prompt] = texture_qty

    if material_str.find(file_name) != -1:
        return file_name

    # model works only with 512x512 image size
    global pipe
    print("Generating texture file: ", file_name)
    full_prompt = "pbd " + prompt + ", seamless texture"
    tex = pipe(full_prompt).images[0]

    save_texture(tex, file_name)

    return file_name


def create_file():
    global material_str

    with open(config.data["work_path"] + "magen_generated.material", "w") as material_file:
        material_file.write(material_str)

    ror_zip_file.add_to_zip_file_list("magen_generated.material")


def save_texture(tex, name):
    global material_str

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
