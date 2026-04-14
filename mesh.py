import xml.etree.ElementTree as ElementTree
from shapely import MultiPoint


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


def get_shape(xml_file_path):
    tree = ElementTree.parse(xml_file_path)
    root = tree.getroot()
    position = root.findall('.//position')

    xml_points = []
    for p in position:
        xml_points.append([p.attrib['x'], p.attrib['y']])

    return MultiPoint(xml_points)
