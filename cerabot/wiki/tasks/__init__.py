from cerabot.wiki import page

class Task(object):
    """Base class for all of Cerabot's tasks."""
    name = None
    task = 0

    def __init__(self, bot):
        """Constructor for new classes."""
        self._bot = bot
        self.site = self._bot.site
        self.summary = self._bot.config["wiki"]["summary"]
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
        run_page = self._bot.config["wiki"]["run_base"]
        run_page = run_page.format(task=self.task)
        page_ = page.Page(self.site, run_page)
        text = page_.content
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
            return self.summary.format(task=self.task, comment=default)
        else:
            return self.summary.format(task=self.task, comment=comment)

    def __repr__(self):
        res = u"Task(name={0}, task={1})"
        return res.format(self.name, self.task)

    def __str__(self):
        res = u"<Task(name={0}, task={1})>"
        return res.format(self.name, self.task)
