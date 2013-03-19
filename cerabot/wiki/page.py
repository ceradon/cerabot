import sys
from .api import Site

__all__ = ["Page"]

class Page(object):
    """Object represents a single page on the wiki.
    On initiation, loads information that could be useful."""

    def __init__(self):
