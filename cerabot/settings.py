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
        self.settings['summary'] = u"Task {task}: {comment}. "+ \
                "([[User:Cerabot/Run/Task {task}|bot]])"