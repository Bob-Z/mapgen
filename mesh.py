import xml.etree.ElementTree as ElementTree

def get_height(xml_file_path):
    tree = ElementTree.parse(xml_file_path)
    root = tree.getroot()
    position = root.findall('.//position')
    min_z = 1000000.0
    max_z = -1000000.0
    for p in position:
        z = float(p.attrib['z'])
        if z < min_z:
            min_z = z
            continue
        if z > max_z:
            max_z = z

    height = max_z - min_z

    return height


def get_extreme_x_y(xml_file_path):
    tree = ElementTree.parse(xml_file_path)
    root = tree.getroot()
    position = root.findall('.//position')

    min_y = 90.0
    max_y = -90.0
    min_x = 180.0
    max_x = -180.0

    min_y_x = 0.0
    max_y_x = 0.0
    min_x_y = 0.0
    max_x_y = 0.0

    for p in position:
        x = float(p.attrib['x'])
        y = float(p.attrib['y'])

        if y < min_y:
            min_y = y
            min_y_x = x
        if y > max_y:
            max_y = y
            max_y_x = x

        if x < min_x:
            min_x = x
            min_x_y = y
        if x > max_x:
            max_x = x
            max_x_y = y

    return (min_x, min_x_y), (max_x, max_x_y), (min_y, min_y_x), (max_y, max_y_x)

