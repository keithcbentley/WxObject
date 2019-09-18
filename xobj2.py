import re

import xml.etree.ElementTree as ET

xobj_namespace = "http://namespace.xobj.org/xobj"


def is_xobj_namespace(xobjtag):
    return xobjtag.namespace == xobj_namespace


class XobjTag:
    default_namespace = None

    def __init__(self, namespace, prefix, name):
        self.namespace = namespace if namespace is not None else XobjTag.default_namespace
        self.prefix = prefix
        self.name = name

    def __str__(self):
        namespace = '{' + (self.namespace if self.namespace else '') + '}'
        prefix = (self.prefix + '.') if self.prefix else ''
        name = self.name if self.name else ''
        return namespace + prefix + name

    @staticmethod
    def new_from_namespace_first_second(namespace, first, second):
        if second is None:
            prefix = None
            name = first
        else:
            prefix = first
            name = second
        return XobjTag(namespace, prefix, name)

    @staticmethod
    def new_from_string(name):
        pattern = r'(\{(?P<namespace>.*)\})?(?P<first>[^\.]*)(\.(?P<second>.*))?'
        match = re.match(pattern, name)
        namespace = match['namespace']
        first = match['first']
        second = match['second']
        return XobjTag.new_from_namespace_first_second(namespace, first, second)

    @staticmethod
    def new_from_tuple(t):
        return XobjTag(t[0], t[1], t[2])

    def as_tuple(self):
        return self.namespace, self.prefix, self.name

    def has_namespace(self, namespace=None):
        if namespace is None:
            return self.namespace is not None
        return self.namespace == namespace

    def has_prefix(self, prefix=None):
        if prefix is None:
            return self.prefix is not None
        return self.prefix == prefix

    def has_name(self, name=None):
        if name is None:
            return self.name is not None
        return self.name == name


class Xobj2:
    def __init__(self, all_namespaces, xobjects):
        self.all_namespaces = all_namespaces
        if self.all_namespaces is None:
            self.all_namespaces = {'': xobj_namespace}
        self.all_namespaces['xobj'] = xobj_namespace
        self.element_tree = None
        self.xobjects = xobjects

    def instantiate_from_file(self, filename):
        self.element_tree = ET.parse(filename)
        root = self.element_tree.getroot()
        self.process_xml_element(root)

    def process_xml_element(self, element):
        this_xobjtag = XobjTag.new_from_string(element.tag)
        if this_xobjtag.namespace != xobj_namespace:
            self.xobjects.on_element(element, this_xobjtag.namespace, this_xobjtag.prefix, this_xobjtag.name)
        for child_element in element:
            child_xobjtag = XobjTag.new_from_string(child_element.tag)
            if child_xobjtag.namespace == xobj_namespace:
                print('special xobj processing')
            else:
                self.process_xml_element(child_element)
        return
