import yaml
from collections import OrderedDict

__all__ = ["OrderedLoader", "OrderedDumper"]

class OrderedLoader(yaml.Loader):
    """A YAML loader that loads mappings into ordered dictionaries."""

    def __init__(self, *args, **kwargs):
        super(OrderedLoader, self).__init__(*args, **kwargs)
        constructor = type(self).construct_yaml_map
        self.add_constructor(u"tag:yaml.org,2002:map", constructor)
        self.add_constructor(u"tag:yaml.org,2002:omap", constructor)

    def construct_yaml_map(self, node):
        data = OrderedDict()
        yield data
        value = self.construct_mapping(node)
        data.update(value)

    def construct_mapping(self, node, deep=False):
        if isinstance(node, yaml.MappingNode):
            self.flatten_mapping(node)
        else:
            raise yaml.constructor.ConstructorError(None, None,
                "expected a mapping node, but found {0}".format(node.id),
                node.start_mark)

        mapping = OrderedDict()
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError, exc:
                raise yaml.constructor.ConstructorError(
                    "while constructing a mapping", node.start_mark,
                    "found unacceptable key ({0})".format(exc),
                    key_node.start_mark)
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping


class OrderedDumper(yaml.SafeDumper):
    """A YAML dumper that dumps ordered dictionaries into mappings."""

    def __init__(self, *args, **kwargs):
        super(OrderedDumper, self).__init__(*args, **kwargs)
        self.add_representer(OrderedDict, type(self).represent_dict)

    def represent_mapping(self, tag, mapping, flow_style=None):
        value = []
        node = yaml.MappingNode(tag, value, flow_style=flow_style)
        if self.alias_key is not None:
            self.represented_objects[self.alias_key] = node
        best_style = True
        if hasattr(mapping, "items"):
            mapping = list(mapping.items())
        for item_key, item_value in mapping:
            node_key = self.represent_data(item_key)
            node_value = self.represent_data(item_value)
            if not (isinstance(node_key, yaml.ScalarNode) and not
                    node_key.style):
                best_style = False
            if not (isinstance(node_value, yaml.ScalarNode) and not
                    node_value.style):
                best_style = False
            value.append((node_key, node_value))
        if flow_style is None:
            if self.default_flow_style is not None:
                node.flow_style = self.default_flow_style
            else:
                node.flow_style = best_style
        return node