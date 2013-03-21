import sys
import time
import collections
import os.path as path
from cerabot import settings
from cerabot import exceptions
from .manager import CommandManager
from cerabot.irc import rc
from cerabot.irc import parser
from cerabot.irc import connection

__all__ = ["IRC"]

class IRC(connection.Connection):
    """Starts an irc connection from the data in the config."""
    def __init__(self, rc_watch=False, _line_parser=None):
        """Main frontend component of the IRC module for Cerabot. 
        Loads connection, parses and runscommands when called, 
        imports all commands."""
        self.settings = settings.Settings().settings
        self._last_conn_check = 0
        self._manager = CommandManager()
        self._line_parser = _line_parser
        self._nick = self.settings['irc_nick']
        dir = path.isfile(path.join(path.dirname(__file__), 
                self.settings["passwd_file"]))
        if self.settings['irc_passwd']:
            self._passwd = self.settings['passwd']
        elif self.settings['passwd_file'] and dir:
            i = path.join(path.dirname(__file__), self.settings["passwd_file"])
            file = open(i, 'r')
            contents = file.read()
            file.close()
            if contents.strip():
                self._passwd = contents
            else:
                #If there is no password, leave it alone
                #It was problably meant to be that way.
                self._passwd = ""
        self._real_name = self.settings['irc_name']
        self._ident = self.settings['irc_ident']
        self.rc_watch = rc_watch
        if self.rc_watch:
            self._host = self.settings['rc_server'][0]
            self._port = self.settings['rc_server'][1]
            super(IRC, self).__init__(self._nick, self._passwd,
                  self._host, self._port, self._real_name, self._ident,
                  join_startup_chans=False, no_login=True)
        elif not self.rc_watch:
            self._host = self.settings['irc_server'][0]
            self._port = self.settings['irc_server'][1]
            super(IRC, self).__init__(self._nick, self._passwd,
                  self._host, self._port, self._real_name, self._ident)

    def start_conn(self):
        """Connect to irc, loop() over all IRC data, calling _process_line() 
        for each line in IRC, and keeps the connection alive."""
        self.connect()
        if self.is_running:
            self.loop()

        while self.is_running:
            self.stayin_alive()
            self._last_conn_check = time.time()
            time.sleep(320)

    def _process_line(self, line):
        """Processes a single line from IRC."""
        data = parser.Parser(line, self._nick)
        result = data._load()
        if not result:
            return
        if self._line_parser:
            self._line_parser(line, data)
        else:
            return self._manager.call(data.command_name, data)

    def get_hooks(self, name):
        """Get all the hooks that can be used to call a command
        from IRC."""
        if not name in self._manager.resources.keys():
            raise ValueError("{0} is not a valid command.".format(name))
        return getattr(self._manager.resources[name], "hooks")

    def get_docs(self, name):
        """Get the help documentation of a command."""
        if not name in self._manager.resources.keys():
            raise ValueError("{0} is not a valid command.".format(name))
        return getattr(self._manager.resources[name], "help_docs")

    def get_required_args(self, name):
        """Gets the amount of required arguments for a command."""
        if not name in self._manager.resources.keys():
            raise ValueError("{0} is not a valid command.".format(name))
        return getattr(self._manager.resources[name], "req_args")

    def __repr__(self):
        """Reutrn a canonical string representation of IRC."""
        return u"IRC(server=({0!r}, {1!r}), nick={2!r}, realname={3!r}"+ \
                "ident=4!r)".format(self._host, unicode(self.port), self._nick,
                self._real_name, self._ident)

    def __str__(self):
        """Return a prettier string representation of IRC."""
        res = u"<IRC ({0!r}, {1!r} with nickname {2!r} and ident {3!r})>"
        return res.format(self._host, unicode(self._port), self._nick, 
                self._ident)

if __name__ == '__main__':
    irc = IRC()
    irc.start_conn()
