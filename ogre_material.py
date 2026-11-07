import config
import ror_zip_file
import PIL
import webcolors
import cache

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
        print("Not enough GPU RAM. Texture generation disabled. Using cached textures if available")
        print()
        pipe = None

material_str = {}

texture_qty_by_material = {}


def create_material(base, tags, material_file_name="mapgen_generated.material", hint=None):
    if config.data["generate_ai_texture"] is False:
        return create_material_color(tags, material_file_name, hint)

    return create_ai_texture(generate_prompt(base, tags, hint), material_file_name, tags)


def generate_prompt(default_material, tags, hint):
    material = default_material

    if hint is not None:
        if hint == "building":
            if "building:material" in tags:
                materials = tags["building:material"].replace(",", ";").split(";")
                material = materials[0]
            elif "material" in tags:
                materials = tags["material"].replace(",", ";").split(";")
                material = materials[0]

            if "building:colour" in tags:
                if tags["building:colour"][0] != '#':
                    material = tags["building:colour"] + " " + material
                else:
                    material = get_color_name(tags["building:colour"]) + " " + material
            elif "colour" in tags:
                if tags["colour"][0] != '#':
                    material = tags["colour"] + " " + material
                else:
                    material = get_color_name(tags["colour"]) + " " + material

        elif hint == "roof":
            if "roof:material" in tags:
                materials = tags["roof:material"].replace(",", ";").split(";")
                material = materials[0]

            if "roof:colour" in tags:
                if tags["roof:colour"][0] != '#':
                    material = tags["roof:colour"] + " " + material
                else:
                    material = get_color_name(tags["roof:colour"]) + " " + material
        else:
            print("Error unknown hint", hint)
    else:
        if "building:material" in tags:
            materials = tags["building:material"].replace(",", ";").split(";")
            material = materials[0]
        elif "material" in tags:
            materials = tags["material"].replace(",", ";").split(";")
            material = materials[0]
        elif "roof:material" in tags:
            materials = tags["roof:material"].replace(",", ";").split(";")
            material = materials[0]

        if "colour" in tags:
            if tags["colour"][0] != '#':
                material = tags["colour"] + " " + material
            else:
                material = get_color_name(tags["colour"]) + " " + material
        elif "building:colour" in tags:
            if tags["building:colour"][0] != '#':
                material = tags["building:colour"] + " " + material
            else:
                material = get_color_name(tags["building:colour"]) + " " + material
        elif "roof:colour" in tags:
            if tags["roof:colour"][0] != '#':
                material = tags["roof:colour"] + " " + material
            else:
                material = get_color_name(tags["roof:colour"]) + " " + material

    if "fence_type" in tags:
        materials = tags["fence_type"].replace(",", ";").split(";")
        if materials[0] != material:
            material = material + " " + materials[0]

    return material


def create_material_color(tags, material_file_name, hint=None):
    colour = None
    if "colour" in tags:
        colour = tags["colour"]

    if hint is not None:
        if hint == "building":
            if "building:colour" in tags:
                colour = tags["building:colour"]
        elif hint == "roof":
            if "roof:colour" in tags:
                colour = tags["roof:colour"]
        else:
            print("Error unknown hint", hint)
    else:
        if "building:colour" in tags:
            colour = tags["building:colour"]
        if "roof:colour" in tags:
            colour = tags["roof:colour"]

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

    if material_file_name in material_str and material_str[material_file_name].find(name) != -1:
        return name

    # Create texture file
    try:
        tex = PIL.Image.new(mode="RGB", size=(1, 1), color=colour)
    except ValueError:
        print("Unsupported colour:", colour[1:])
        return None

    save_texture(tex, name, material_file_name)

    return name


def create_ai_texture(prompt, material_file_name, tags):
    file_name = prompt.replace(" ", "_")
    file_name = "texture_" + file_name

    texture_qty = 0
    if prompt in texture_qty_by_material:
        texture_qty = texture_qty_by_material[prompt]

    file_name = file_name + "_" + str(texture_qty % config.data["max_texture_by_material"])

    texture_qty += 1
    texture_qty_by_material[prompt] = texture_qty

    if material_file_name in material_str and material_str[material_file_name].find(file_name) != -1:
        return file_name

    tex = cache.load_texture(file_name)
    if tex is None:
        global pipe
        if pipe is None:
            return create_material_color(tags, material_file_name)
        # model works only with 512x512 image size
        print("Generating texture file: ", file_name)
        full_prompt = "pbd " + prompt + ", seamless texture"
        tex = pipe(full_prompt).images[0]
        cache.save_texture(tex, file_name)
    else:
        print("Using cached texture:", file_name)

    save_texture(tex, file_name, material_file_name)

    return file_name


def create_file():
    global material_str

    if len(material_str) > 0:
        for key, value in material_str.items():
            with open(config.data["work_path"] + key, "w") as material_file:
                material_file.write(value)

        ror_zip_file.add_to_zip_file_list("mapgen_generated.material")


def save_texture(tex, filename, material_file_name):
    global material_str

    tex.save(config.data["work_path"] + filename + ".png", "PNG")
    ror_zip_file.add_to_zip_file_list(filename + ".png")

    if material_file_name not in material_str:
        material_str[material_file_name] = "import * from \"managed_mats.material\" \n\n"

    # Add to material file
    material_str[material_file_name] += "material " + filename + " : RoR/Managed_Mats/Base\n"
    material_str[material_file_name] += "{\n"
    material_str[material_file_name] += "   technique BaseTechnique\n"
    material_str[material_file_name] += "   {\n"
    material_str[material_file_name] += "       pass BaseRender\n"
    material_str[material_file_name] += "       {\n"
    material_str[material_file_name] += "           cull_hardware none\n"
    material_str[material_file_name] += "           cull_software none\n"
    material_str[material_file_name] += "           texture_unit Diffuse_Map\n"
    material_str[material_file_name] += "           {\n"
    material_str[material_file_name] += "               texture " + filename + ".png\n"
    material_str[material_file_name] += "           }\n"
    material_str[material_file_name] += "       }\n"
    material_str[material_file_name] += "   }\n"
    material_str[material_file_name] += "}\n"
    material_str[material_file_name] += "\n"


def get_color_name(hex_value):
    try:
        # Get the color name directly
        return webcolors.hex_to_name(hex_value)
    except ValueError:
        # If exact match not found, find the closest color
        return closest_color(hex_value)


def closest_color(hex_value):
    requested_color = webcolors.hex_to_rgb(hex_value)
    min_colors = {}
    for norm in webcolors._definitions._hex_to_names.items():
        for key, name in norm[1].items():
            r_c, g_c, b_c = webcolors.hex_to_rgb(key)
            rd = (r_c - requested_color[0]) ** 2
            gd = (g_c - requested_color[1]) ** 2
            bd = (b_c - requested_color[2]) ** 2
            min_colors[(rd + gd + bd)] = name
    return min_colors[min(min_colors.keys())]
