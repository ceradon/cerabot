import sys
import time
import os.path as path
import wikitools.wiki as wiki
import wikitools.page as page
from cerabot import settings
from cerabot import exceptions

class Bot(object):
    """Base class for all of Cerabot's tasks."""
    name = None
    task = 0

    def __init__(self):
        """Initiates the Bot class."""
        #Builds several important variales.
        self.is_logged_in = False
        self.site_api = None
        self.wiki = None
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
        self.wiki = wiki.Wiki(self.site_api)
        
        #Login to site API
        self.wiki.login(self.user, self.passwd)
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

    def run_page_enabled(self):
        """Checks if the run page for
        Cerabot is enabled.
        """
        run_page = self.settings['run_base']
        run_page = run_page.format(task=self.task)
        page_ = page.Page(self.wiki, run_page)
        text = page_.getWikiText()
        if not text.lower() == 'yes':
            raise exceptions.RunPageDisabledError("Run page is disabled.")
        else:
            return True

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
