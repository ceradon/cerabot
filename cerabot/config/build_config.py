import sys
import yaml
from .ordered import OrderedDumper
from collections import OrderedDict

class BuildConfig(object):
    """Makes a config file from command line input."""
    def __init__(self):
        self.data = OrderedDict([])
