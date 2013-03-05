import sys

class Settings(object):
    def __init__(self):
        """Initiate the `settings` dictionary"""
        self.settings = {}

        #Bot settings
        self.settings['user'] = u"Cerabot"
        self.settings['site'] = [(u"wikipedia", u"en")]
        self.settings['passwd'] = u""
        self.settings['passwd_file'] = u".passwd"

        #Wikipedia settings
        self.settings['run_base'] = u"User:Cerabot/Run/Task {task}"
        self.settings['summary'] = u"Task {task}: {comment}. "
        self.settings['summary'] += "([[User:Cerabot/Run/Task {task}|bot]])"
        
        #IRC settings
        self.settings['irc_nick'] = u"Cerabot"
        self.settings['irc_passwd'] = u""
        self.settings['irc_server'] = u"irc.freenode.net", 6667
        self.settings['irc_name'] = u"IRC extension to Wikipedia robot Cerabot."
        self.settings['irc_ident'] = u"cerabot"
        self.settings['join_on_startup'] = ["##cerabot", "##ceradon"]
