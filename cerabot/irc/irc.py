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
    def __init__(self, rc_watch=False, _line_parser=None):
        """Main frontend component of the IRC module
        for Cerabot. Loads connection, parses and runs
        commands when called, imports all commands."""
        self.settings = settings.Settings().settings
        self._last_conn_check = 0
        self.commands = None
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
            self.assemble_commands()
        self.connect()

    def _load_conn(self):
        """loop() over all IRC data, calling _process_line() for
        each line in IRC, and keeps the connection alive."""
        if self.is_running:
            self.loop()

        while self.is_running:
            self.stayin_alive()
            self._last_conn_check = time.time()
            time.sleep(320)

    def assemble_commands(self):
        """Assembles all the commands we'll be using, putting the
        name of the command and each command's hooks into one 
        dictionary."""
        self.commands = {}

        for name in self._manager.resources.keys():
            docs = self.get_docs(name)
            hooks = self.get_hooks(name)
            self.commands.update({name:hooks.insert(0, name)})

    def _process_line(self, line):
        """Processes a single line from IRC."""
        parse = parser.Parser(line, self._nick)
        result = parse._load()
        if not result:
            return
        if self._line_parser:
            self._line_parser(line, parse)
        else:
            self._process_data(line, parse)
        
    def _process_data(self, line, parse):
        """Processes a single line of data when _line_parser
        is not specified."""
        if parse.is_command and parse.command_name in self.commands.values():
            command = self._manager.resources[parse.command_name]
            a = command.has_args
            if a[0]:
                self.manager.call(parse.command_name)
            else:
                if a[1] == "insufficient":
                    e = u"<bold>{0}<normal>, You have not provided "+ \
                            "enough arguments to {1}."
                    self.reply(e.format(parse.nick, parse.command_name),
                            parse)
                elif a[1] == "excess":
                    e = u"<bold>{0}<normal>, {1} arguments required "+ \
                            "for {2}, {3} given."
                    self.reply(e.format(parse.nick, unicode(parse.req_args), 
                            len(parse.args)))

    def get_hooks(self, name):
        """Get all the hooks that can be used to call a command
        from IRC."""
        if not name in self.manager.resources.keys():
            raise ValueError("{0} is not a valid command.".format(name))
        return getattr(self.manager.resources[name], "hooks")

    def get_docs(self, name):
        """Get the help documentation of a command."""
        if not name in self.manager.resources.keys():
            raise ValueError("{0} is not a valid command.".format(name))
        return getattr(self.manager.resources[name], "help_docs")

    def get_required_args(self, name):
        """Gets the amount of required arguments for a command."""
        if not name in self.manager.resources.keys():
            raise ValueError("{0} is not a valid command.".format(name))
        return getattr(self.manager.resources[name], "req_args")

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
    irc._load_conn()
