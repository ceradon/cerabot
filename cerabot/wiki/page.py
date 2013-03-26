import sys
from .api import Site

__all__ = ["Page"]

class Page(object):
    """Object represents a single page on the wiki.
    On initiation, loads information that could be useful."""

    def __init__(self, site, title="", pageid=0, follow_redirects=False):
        self.site = site
        self._title = title
        self._pageid = pageid
        self._follow_redirects = follow redirects

        self._exists = 0
        self._is_redirect = False
        self._is_talkpage = False
        self._last_revid = None
        self._creator = None
        self._level = None
        self._content = None

        self._prefix = None
        self._namespace = 0

    def _load(self):
        """Loads the attributes of this page."""
        raise NotImplementedError()
