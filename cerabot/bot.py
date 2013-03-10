import re
import sys
import json
import time
import datetime
import os.path as path
from cerabot import settings
from urllib import urlencode
from cerabot import exceptions
from urllib2 import Request, urlopen, HTTPError, URLError

#Import `wikitools` and `mwparserfromhell`
#packages.
import wikitools.api as api
import wikitools.wiki as wiki
import wikitools.page as page
import wikitools.user as user
import wikitools.wikifile as file
import wikitools.category as category
import mwparserfromhell as parser

class Bot(object):
    """Base class for all of Cerabot's tasks."""
    name = None
    task = 0

    def __init__(self):
        """Initiates the Bot class."""
        #Builds several important variales.
        self.is_logged_in = False
        self.site_api = None
        self.site = None
        self.settings = settings.Settings().settings
        if not self.settings:
            raise exceptions.MissingSettingsError("Variable `settings` "+
                                                  "is empty")
        self.summary = self.settings['summary']

        #Assemble bot variables
        self.user = self.settings['user']
        if self.settings['passwd']:
            self.passwd = self.settings['passwd']
        elif not self.settings['passwd'] and \
                self.settings['passwd_file']:
            if path.isfile(self.settings['passwd_file']):
                file = open(self.settings['passwd_file'], 'r')
                self.passwd = file.read().rstrip()
                file.close()
            else:
                raise exceptions.NoPasswordError("`passwd_file` "+
                        "does not exist")
        elif not self.settings['passwd'] and \
                not self.settings['passwd_file']:
            raise exceptions.NoPasswordError("Variables `passwd` "+
                    "and `passwd_file` were not defined")

        #Build site API URL
        self.site_api = self._build_site_api(
                self.settings['site'][0])
        self.site = wiki.Wiki(self.site_api)

        #Setup some convenience functions for
        #tasks to use:
        self.access_api = api
        self.access_wiki = wiki
        self.access_page = page
        self.access_user = user
        self.access_file = file
        self.access_category = category
        self.parser = parser

        #Login to site API
        self.site.login(self.user, self.passwd)
        self.is_logged_in = True
        self.setup()

    def setup(self):
        """Called immediately after Bot is initiated.
        Idles by default.
        """
        pass

    def run(self):
        """Main method by which the task does stuff and also
        serves as the main entry point for the task.
        """
        pass

    def edit_time(self, page):
        try:
            base_url = "http://en.wikipedia.org/w/api.php"
            user_agent = self.settings["user_agent"]
            data = {'action':'query',
                    'prop':'revisions',
                    'titles':page,
                    'format':'json',
                    'rvprop':'timestamp|user'}
            args = urlencode(data)
            headers = {'User-Agent':user_agent}
            request = Request(base_url, args, headers)
            send_data = urlopen(request)
            response = unicode(send_data.read())
            return_data = json.loads(response)
            result = return_data["query"]["pages"].values()[0]
            edit_time = result["revisions"][0]["timestamp"]
            date_time = datetime.datetime.strptime(edit_time, 
                    '%Y-%m-%dT%H:%M:%SZ')
        except HTTPError as e:
            print "The server could not fulfill our request."+ \
                    "Closed with error code: {0}".format(e.code)
            return None
        except URLError as e:
            print "Unable to connect to server, Retuned: {0}".format(
                e.reason)
            return None
        return date_time

    def check_exclusion(self, page, text=None):
        if not text:
            page_obj = page.Page(self.site, page)
            text = page_obj.getWikiText()
        regex = "\{\{\s*(no)?bots\s*\|?((deny|allow)=(.*?))?\}\}"
        re_compile = re.search(regex, text)
        if re_compile.group(1):
            return False
        if (self.user.lower() in re_compile.group(4).lower()):
            if re_compile.group(3) == "allow":
                return True
            if re_compile.group(3) == "deny":
                return False

    def run_page_enabled(self):
        """Checks if the run page for
        Cerabot is enabled.
        """
        run_page = self.settings['run_base']
        run_page = run_page.format(task=self.task)
        page_ = page.Page(self.site, run_page)
        text = page_.getWikiText()
        if not text.lower() == 'yes':
            raise exceptions.RunPageDisabledError("Run page is disabled.")
        else:
            return

    def build_summary(self, comment=None):
        """Builds the summary for every edit 
        the task will make. Param `comment` is
        an optional message. Defaults to 
        'Automated edit by [[User:Cerabot]]'
        """
        default = "Automated edit by [[User:Cerabot]]"
        if not comment:
            return self.summary.format(task=self.task,  
                    comment=default)
        else:
            return self.summary.format(task=self.task, 
                    comment=comment)

    def _build_site_api(self, args):
        """Builds the site's api URL

        Param `args` must be a dictionary
        In the format of `("{site}", "{wiki}")`
        """
        template = "http://{lang}.{site}.org/w/api.php"
        if not type(args) == tuple:
            print "Error: Variable `args` must be a tuple"
            return
        else:
            res = template.format(site=args[0], lang=args[1])
        return res

    def __repr__(self):
        """Return the canonical string representation of the Task."""
        res = "Bot(name={0!r}, task={1!r})"
        return res.format(self.name, self.task)

    def __str__(self):
        """Return a prettier string representation of the Task."""
        res = "<Bot {0} (Task {1})>"
        return res.format(self.name, self.task)
