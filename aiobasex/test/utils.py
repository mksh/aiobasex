from xml.dom import minidom
from xml.dom.minidom import Node


def remove_blanks(node):
    for x in node.childNodes:
        if x.nodeType == Node.TEXT_NODE:
            if x.nodeValue:
                x.nodeValue = x.nodeValue.strip()
        elif x.nodeType == Node.ELEMENT_NODE:
            remove_blanks(x)


def get_cleaned_node(node_xml):
    """Strip text values in XML."""
    parsed = minidom.parseString(node_xml)
    remove_blanks(parsed)
    parsed.normalize()
    ret = parsed.toxml('utf-8')
    return ret.decode('utf-8')
