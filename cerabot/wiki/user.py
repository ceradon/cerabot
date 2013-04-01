import sys
from ipaddress import ip_address
from dateutil.parser import parse
from cerabot.wiki.page import Page

class User(object):
    """Object representing a single user on the wiki."""

    def __init__(self, site, name):
        """Constructs the User object."""
        self._site = site
        self._user = name

        self._load_attributes()

    def _load_attributes(self):
        """Loads all attributes relating to our current user."""
        props = "blockinfo|groups|rights|editcount|registration|emailable|gender"
        query = {"action":"query", "list":"users", "ususers":self._user,
            "usprops":props}
        res = self._site.query(query)
        result = res["query"]["users"][0]

        # If the name was entered oddly, normalize it:
        self._user = result["name"]

        try:
            self._userid = result["userid"]
        except KeyError:
            self._exists = False
            return

        self._exists = True

        try:
            self._blocked = {
                "by": result["blockedby"],
                "reason": result["blockreason"],
                "expiry": result["blockexpiry"]
            }
        except KeyError:
            self._blocked = False

        self._groups = result["groups"]
        try:
            self._rights = result["rights"].values()
        except AttributeError:
            self._rights = result["rights"]
        self._editcount = result["editcount"]

        reg = result["registration"]
        try:
            self._registration = parse(reg)
        except TypeError:
            # In case the API doesn't give is a date.
            self._registration = parse("0")

        try:
            result["emailable"]
        except KeyError:
            self._emailable = False
        else:
            self._emailable = True

        self._gender = result["gender"]

    @property
    def user(self):
        return sself._user

    @property
    def userid(self):
        return self._userid

    @property
    def exists(selF):
        return self._exists

    @property
    def blocked(self):
        return self._blocked

    @property
    def groups(self):
        return self._groups

    @property
    def rights(self):
        return self._rights

    @property
    def editcount(self):
        return self._editcount

    @property
    def registration(self):
        return self._registration

    @property
    def emailable(self):
        return self._emailable

    @property
    def gender(self):
        return self._gender

    @property
    def is_ip(self):
        try:
            is_ip = bool(ip_address(self.user))
        except ValueError:
            is_ip = False
        return is_ip

    @property
    def userpage(self):
        if self._userpage:
            return self._userpage
        else:
            self._userpage = Page("User:{0}".format(self.user))
        return self._userpage

    @property
    def talkpage(self):
        if self._talkpage:
            return self._talkpage
        else:
            self._talkpage = Page("User talk:{0}".format(self.user))
        return self._talkpage
