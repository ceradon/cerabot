import sys
from .pag import Page

class File(Page):
    """Object represents a single file on the wiki."""

    def load_attributes(self):
        """Loads all attributes of the current file."""
        raise NotImplementedError()
