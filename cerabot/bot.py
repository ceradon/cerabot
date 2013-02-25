import sys
from .. import cerabot

class Bot(object):
    """Base class for a of Cerabot's tasks."""
    name = None
    task = 0

    def __init__(self):
        """Initiates the Bot class."""
        self.is_logged_in = False
        self.site_api = None
        self.wiki = None
        self.settings = settings.Settings().settings
        if not self.settings:
            raise MissingSettingsError("Variable `settings` is empty")

        #Assemble bot variables
        self.user = self.settings['user']
        if self.settings['passwd']:
            self.passwd = self.settings['passwd']
        elif not self.settings['passwd'] and
                self.settings['passwd_file']:
            file = open(self.settings['passwd_file'], 'r')
            self.passwd = file.read()
            file.close()
        elif not self.settings['passwd'] and 
                not self.settings['passwd_file']:
            raise NoPasswordError("Variables `passwd` and "+
                    "`passwd_file` were not defined")

        #Build site API URL
        self.site_api = self._build_site_api(
                self.settings['site'][0])
        self.wiki = wiki.Wiki(self.site_api)
        
        #Login to site API
        self.wiki.login(self.user, self.passwd)

    def _build_site_api(self, args):
        """Builds the site's api URL

        Param `args` must be a dictionary
        In th format of `("{site}", "{wiki}")`
        """
        template = "http://{lang}.{site}.org/w/api.php"
        if not type(args) == tuple:
            print "Error: Variable `args` must be a tuple"
            return
        else:
            template = template.format(site=args[0], lang=args[1])
        return

    def run_page_enabled(self):
        """Checks if the run page for
        Cerabot is enabled.
        """
        run_page = self.settings['run_base']
        run_page = run_page.format(task=self.task)
        page_ = page.Page(self.wiki, run_page)
        text = page_.getWikiText()
        if not text == 'yes':
            raise RunPageDisabledError("Run page is disabled.")
        else:
            return True
