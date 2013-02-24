import sys

class Settings(object):
    #Initiate the settings dictionary
    settings = {}

    #Bot settings
    settings['user'] = u"Cerabot"
    settings['site'] = {(wikipedia, en)}
    settings['passwd'] = u""
    settings['passwd_file'] = u".passwd"
    
    #Wikipedia settings
    settings['run_base'] = u"User:Cerabot/Run/Task {task}"
    settings['summary_end'] = u". ([[User:Cerabot/Run/Task {task}|bot]])"
