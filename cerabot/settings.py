import sys
from platform import version, machine, linux_distribution as dist, python_version as pyv

class Settings(object):
    def __init__(self):
        """Initiate the `settings` dictionary"""
        self.settings = {}
        self.settings["user_agent"] = u"Cerabot/0.1 (Python/{0}; {1}; {2}; {3}; {4})"
        self.settings["user_agent"] = self.settings["user_agent"].format(pyv(), dist()[0],
            version(), dist()[1], machine())
        self.settings["wiki"] = {}
        self.settings["irc"] = {}
        self.settings["sql"] = {}
        self.settings["watcher"] = {}

        #Wiki settings
        self.settings["wiki"]["user"] = u"Cerabot"
        self.settings["wiki"]["site"] = [(u"wikipedia", u"en")]
        self.settings["wiki"]["passwd"] = u""
        self.settings["wiki"]["passwd_file"] = u".passwd"
        self.settings["wiki"]["run_base"] = u"User:Cerabot/Run/Task {task}"
        self.settings["wiki"]["summary"] = u"Task {task}: {comment}. "
        self.settings["wiki"]["summary"] += "([[User:Cerabot/Run/Task {task}|bot]])"
        
        #IRC settings
        self.settings["irc"]["nick"] = u"Cerabot"
        self.settings["irc"]["passwd"] = u""
        self.settings["irc"]["passwd_file"] = u".passwd"
        self.settings["irc"]["server"] = u"irc.freenode.net", 6667
        self.settings["irc"]["realname"] = u"IRC extension to Pyhton robot Cerabot."
        self.settings["irc"]["ident"] = u"cerabot"
        self.settings["irc"]["channels"] = ["##cerabot", "##ceradon"]

        #Watcher settings
        self.settings["watcher"]["nick"] = u"Cerabot"
        self.settings["watcher"]["server"] = u"irc.wikimedia.org", 6667
        self.settings["watcher"]["realname"] = u"IRC extension to Python robot Cerabot."
        self.settings["watcher"]["ident"] = u"cerabot"
        self.settings["watcher"]["channels"] = ["#en.wikipedia"]

        #Database settings
        self.settings["sql"]["host"] = u"bots-bsql01"
        self.settings["sql"]["port"] = 1433
        self.settings["sql"]["user"] = u"ceradon"
        self.settings["sql"]["password"] = u""
