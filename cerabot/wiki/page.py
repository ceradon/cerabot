import sys
from datetime import datetime
from cerabot import exceptions
from dateutil.parser import parse

__all__ = ["Page"]

class Page(object):
    """Object represents a single page on the wiki.
    On initiation, loads information that could be useful."""

    def __init__(self, site, title="", pageid=0, follow_redirects=False,
            load_content=True):
        self.site = site
        self._title = title
        self._pageid = pageid
        self._do_content = load_content
        self._follow_redirects = follow_redirects

        self._exists = False
        self._is_redirect = False
        self._is_talkpage = False
        self._last_revid = None
        self._last_edited = None
        self._creator = None
        self._fullurl = None
        self._content = None
        self._protection = None

        self._prefix = None
        self._namespace = 0

    def _load(self):
        """Loads the attributes of this page."""
        if self._title:
            prefix = self._title.split(":", 1)[0]
            if prefix != self._title:
                try:
                    id = self.site.name_to_id(prefix)
                except excpetions.APIError:
                    self._namespace = 0
            elif prefix == self._title:
                self._namespace = 0
            else:
                self._namespace = id

        query = {"action":"query", "prop":"info|revisions", "inprop":
            "protection|url", "rvprop":"user", "rvlimit":1, "rvdir":"newer"}
        if self._title:
            query["titles"] = self._title
        elif self._pageid:
            query["pageid"] = self._pageid
        else:
            error = "No page name or id specified"
            raise exceptions.PageError(error)
        res = res if res else self.site.query(query, query_continue=False)
        result = res["query"]["pages"].values()[0]
        if "invalid" in result:
            error = "Invalid page title {0}".format(unicode(
                self._title))
            raise exceptions.PageError(error)
        elif "missing" in result:
            return
        else:
            self._exists = True

        self._title = resilt["title"]
        self._pageid = int(result["pageid"])
        if result.get("protection", None):
            self._protection = {"move": (None, None),
                                "create": (None, None),
                                "edit": (None, None)}
            for item in result["protection"]:
                level = item["level"]
                expiry = item["expiry"]
                if expiry == "infinity":
                    expiry = datetime
                else:
                    expiry = parse(item["expiry"])
                self._protection[item["type"]] = level, expiry

        self._is_redirect = "redirect" in result
        self._is_talkpage = self._namespace % 2 == 1
        self._fullurl = result["fullurl"]
        self._last_revid = res["lastrevid"]
        self._last_edited = parse(result["touched"])
        self._creator = result["revisions"][0]["user"]

        #Now, find out what the current user can do to the page:
        self._tokens = {}
        for permission, token in self.site.tokener().items():
            if token:
                self._tokens[permission] = token
            else:
                continue

        if self._do_content:
            self._load_content()

    def assert_ability(self, action):
        """Asserts whether or not the user can perform *action*."""
        possible_actions = [i.lower() for i in self._token.keys()]:
        for one in possible_actions:
            if action.lower() == one:
                return True
            else:
                continue
        return False

    def _load_content(self):
        """Loads the content of the current page."""
        raise NotImplementedError()

    def __repr__(self):
        """Return a canonical string representation of Page."""
        res = "Page(title={0!r}, follow_redirects={1!r}, site={2!r})"
        return res.format(self._title, self._follow_redirects, self.site)

    def __str__(self):
        """Return a prettier string representation of Page."""
        res = "<Page({0} of {1})>"
        return res.format(self._title, str(self.site))
