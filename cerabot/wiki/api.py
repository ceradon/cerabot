import re
import sys
import time
try:
    import json
except Exception:
    import simplejson as json
try:
    import gzip
except Exception:
    gzip = False
from threading import Lock
from copy import deepcopy
from StringIO import StringIO
from cookielib import CookieJar
from urllib import quote_plus
from cerabot import exceptions
from urlparse import urlparse
from platform import python_version as pyv
from urllib2 import build_opener, HTTPCookieProcessor, URLError

class Site(object):
    """Main point for which interaction with a MediaWiki
    API is made."""
    GITHUB = "https://github.com/ceradon/cerabot"
    USER_AGENT = "Cerabot/{0!r} (wikibot; Python/{1!r}; {2!r})"
    USER_AGENT = USER_AGENT.format("0.1", pyv(), GITHUB)
    config = {"throttle":10,
              "maxlag":10,
              "max_retries":3}

    def __init__(self, name=None, base_url="http://en.wikipedia.org",
            project=None, lang=None, namespaces={}, login=(None, None),
            secure=False, config=None, path=None, user_agent=None):
        self._name = name
        if not project and not lang:
            self._base_url = base_url
        else:
            self._lang = lang
            self._project = project
            self._base_url = "http://{0!r}.{1!r}".format(self._lang,
                    self._project)
            if secure:
                self._base_url = self._base_url.replace("http://", "https://")
        if path:
            self._path = path
        else:
            self._path = "/wiki/"
        self._namespaces = namespaces
        if config:
            self._config = config
        else:
            self._config = self.config
        self._login = login
        self._secure = secure
        if user_agent:
            self._user_agent = user_agent
        else:
            self._user_agent = self.USER_AGENT

        self._throttle, self._maxlag, self._max_retries = self._config.values()
        self._last_query_time = 0
        self.cookie_jar = CookieJar()
        self.api_lock = Lock()
        self.opener = build_opener(HTTPCookieProcessor(self.cookie_jar))
        self.opener.addheaders = [("User-Agent", self._user_agent),
                                  ("Accept-Encoding", "gzip")]
        if login:
            self.login(login)
        self._load()

    def urlencode(self, params):
        """Implement urllib.urlencode() with support for unicode input.
        Thanks to Earwig (Ben Kurtovic) for this code."""
        enc = lambda s: s.encode("utf8") if isinstance(s, unicode) else str(s)
        args = []
        for key, val in params.iteritems():
            key = quote_plus(enc(key))
            val = quote_plus(enc(val))
            args.append(key + "=" + val)
        return "&".join(args)

    def _query(self, params, query_continue=True, tries=0, idle=5):
        """queries the site's API."""
        last_query = time.time() - self._last_query_time
        if last_query < self._throttle:
            throttle = self._throttle - last_query
            print "Throttling: waiting {0} seconds".format(round(throttle, 2))
            time.sleep(throttle)
        params.setdefault("maxlag", self._maxlag)
        params.setdefault("format", "json")
        params["continue"] = ""
        url = ''.join((self._base_url, self._path, "api.php"))
        data = urlencode(params)
        try:
            reply = self.opener.open(url, data)
        except URLError as e:
            if hasattr(e, "code"):
                exc = "API query could not be completed: Error code: {0}"
                exc = exc.format(e.code)
            elif hasattr(e, "reason"):
                exc = "API query could not be completed. Reason: {0}"
                exc = exc.format(e.reason)
            else:
                exc = "API query could not be completed."
            raise exceptions.APIError(exc)
        
        result = reply.read()
        if reply.headers.get("Content-Encoding") == "gzip":
            stream = StringIO(result)
            zipper = gzip.GzipFile(fileobj=stream)
            result = zipper.read()
        
        try:
            res = json.loads(result)
        except ValueError:
            e = "API query failed: JSON could not be loaded"
            raise exceptions.APIError(e)
        
        try:
            code = res["error"]["code"]
            info = res["error"]["info"]
        except (TypeError, ValueError):
            if "continue" in res:
                continue_data = self._handle_query_continue(params, res)
                res["query"][res["query"].keys()[0]].extend(continue_data)
            return res
        
        if code == "maxlag":
            if tries >= self._max_retries:
                e = "Maximum amount of allowed retries has been exhausted."
                raise exception.APIError(e)
            tries += 1
            time.sleep(idle)
            return self._query(params, tries=tries, idle=idle*2)
        else:
            e = "An unknown error occured. Here is the data from the API: {0}"
            return_data = "({0}, {1})".format(code, info)
            error = exceptions.APIError(e.format(return_data))
            error.code, error.info = code, info
            raise error
    
    def _load(self, force=False):
        """Loads the sites attributes. Called automatically on initiation."""
        attrs = [self._name, self._project, self._lang, self._base_url,
                self._path]
        query = {"action":"query", "meta":"siteinfo", "siprop":"general"}

        if not self._namespace or force:
            query["siprop"] += "|namespaces|namespacealiases"
            result = self._query(query)
            for item in result["query"]["namespaces"].values():
                ns_id = item["id"]
                name = item["*"]
                try:
                    canonical = namespace["canonical"]
                except KeyError:
                    self._namespaces[ns_id] = [name]
                else:
                    if name != canonical:
                        self._namespaces[ns_id] = [name, canonical]
                    else:
                        self._namespaces[ns_id] = [name]
            
            for item in result["query"]["namespacealiases"]:
                ns_id = item["id"]
                alias = item["*"]
                self._namespaces[ns_id].append(alias)
        
        result = result["query"]["general"]
        self._name = result["wikiid"]
        self._project = result["sitename"].lower()
        self._lang = result["lang"]
        self._base_url = result["server"]
        self._path = result["scriptpath"]

    def _handle_query_continue(self, request, data):
        """Handle \'query-continues\' in API queries."""
        count = 0
        last_continue = {}
        while "continue" in data:
            query = deepcopy(request)
            query.update(last_continue)
            response = self._query(query)
            last_continue = response["continue"]
            if not all_data:
                all_data = response["query"][list(x["query"])[0]]
            else:
                all_data[0].append(response["query"][list(x["query"])[0]])
        return all_data

    def get_page(self, pagename, follow_redirects=False, pageid=None):
        """Returns an instance of Page for *pagename* with *follow_redirects* and
        *pageid* as arguments, unless *pagename* is a category, then returns a
        Cateogry instance."""
        raise NotImplementedError()

    def get_category(self, catname, follow_redirects=False, pageid=None):
        """Returns an instance of Category for *catname* with *follow_redirects*
        and *pageid* as arguments."""
        raise NotImplementedError()

    def get_user(self, username=None):
        """Returns an instance of User for *username*."""
        raise NotImplementedError()

    @property
    def domain(self):
        """Returns the site's web domain, like \"en.wikipedia.org\""""
        return urlparse(self._base_url).netloc

    def get_username(self):
        """Gets the name of the user that is currently logged into the site's API.
        Simple way to ensure that we are logged in."""
        data = self.query(action="query", meta="userinfo")
        return data["query"]["userinfo"]["name"]

    def get_cookies(self, name, domain):
        for cookie in self.cookie_jar:
            if cookie.name == name and cookie.domain == domain:
                if cookie.is_expired():
                    break
                return cookie

    def save_cookie_jar(self):
        """Attempts to save all changes to our cookiejar after a successful 
        login or logout."""
        if hasattr(self.cookie_jar, "save"):
            try:
                getattr(self._cookiejar, "save")()
            except (NotImplementedError, ValueError):
                pass

    def query(self, params, query_continue=True):
        """Queries the site's API."""
        with self.api_lock:
            self._query(params, query_continue)

    def _login(self, login, token=None, attempts=0):
        """Logs into the site's API."""
        username, password = login
        if token:
            i = self.query(action="login", lgname=username, lgpassword=password,
                    lgtoken=token)
        else:
            i = self.query(action="login", lgname=username, lgpassword=password)

        res = i["login"]["result"]
        if res == "Success":
            self.save_cookie_jar()
        elif res == "NeedToken" and attempts == 0:
            token = i["login"]["token"]
            return self._login(login, token, attempts=1)
        else:
            if res == "Illegal":
                e = "The provided username is illegal."
            elif res == "NotExists":
                e = "The provided username does not exist."
            elif res == "EmptyPass":
                e = "No password was given."
            elif res == "WrongPass" or res == "WrongPluginPass":
                e = "The given password is incorrect."
            else:
                e = "An unknown error occured, API responded with {0)."
                e = e.format(res)
            raise exceptions.APILoginError(e)

    def login(self, login):
        """Public method for logging in to the API."""
        if not login and self._login:
            login = self._login
        else:
            e = "No login data ptovided."
            raise exceptions.APILoginError(e)
        if type(login) == tuple:
            self._login(login)
        else:
            e = "Login data must be in tuple format, got {0}"
            raise exceptions.APILoginError(e.format(type(login)))

    def logout(self):
        """Attempts to logout out the API and clear the cookie jar."""
        self.query(action="logout")
        self.cookie_jar.clear()
        self.save_cookie_jar()

    def tokener(self, args=[]):
        i = re.compile("Action (.*?) is not allowed for the current user")
        valid_args = ["block", "delete", "edit", "email", "import", "move",
                      "options", "patrol", "protect", "unblock", "watch"]
        if not args:
            args = valid_args
        if not type(args) == list:
            return
        query = {"action":"query", "prop":"info", "titles":"Main Page",
                 "intoken":"|".join(args)}
        result = self.query(query)
        res = result["query"]["pages"]
        _tokens = {}
        for key, val in res[0][1][list(x[0][1])[0]].items():
            if key.endswith("token"):
                name = key.find("token")
                _tokens[name] = val
                args.pop(name)
        
        if "warnings" in result:
            if len(args) > 1:
                a = result["warnings"]["info"]["*"].split("\n")
            else:
                a = [result["warnings"]["info"]["*"]]
            for item in a:
                name = i.findall(item)
                name = name.strip("'")
                _tokens[name] = None

        return _tokens
