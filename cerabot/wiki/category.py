import sys
from .page import Page

class Category(Page):
    """Object that represents a single category on a wiki."""

    def load_attributes(self, res=None):
        super().load(res)
        self._members = []
        self._subcats = []
        self._files = []

    def _load_attributes(self, res=None):
        """Loads attributes about our current category."""
        raise NotImplementedError()

    @property
    def members(self):
        return self._members

    @property
    def subcats(self):
        return self._subcats

    @property
    def files(self):
        return self._files

    @property
    def categories(self):
        return self._subcats

    def __repr__(self):
        """Return a canonical string representation of Cateogry."""
        res = "Category(title={0}, site={1})"
        return res.format(self.title, str(self.site))

    def __str__(self):
        res = "<Category(category {0} for site object {1})>"
        return res.format(self.title, str(self.site))
