import sys
import time
import collections
import os.path as path
from cerabot import settings
from cerabot import exceptions
from cerabot.irc import rc
from cerabot.irc import parser
from cerabot.irc import connection

__all__ = ["IRC", "Command"]

class IRC(connection.Connection):
    def __init__(self, rc_watch=False, _line_parser=None):
        """Main frontend component of the IRC module
        for Cerabot. Loads connection, parses and runs
        commands when called, imports all commands."""
        self.settings = settings.Settings().settings
        self._last_conn_check = 0
        self._commands = {}
        self._command_obj = None
        self._command_hooks = {}
        self._line_parser = _line_parser
        self._nick = self.settings['irc_nick']
        if self.settings['irc_passwd']:
            self._passwd = self.settings['passwd']
        elif self.settings['passwd_file'] and \
                path.isfile(self.settings['passwd_file']):
            file = open(self.settings['passwd_file'], 'r')
            contents = file.read()
            file.close()
            if contents.strip():
                self._passwd = contents
            else:
                #If there is no password, leave it alone.
                pass
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
            self._assemble_commands()
            super(IRC, self).__init__(self._nick, self._passwd,
                  self._host, self._port, self._real_name, self._ident)
        self.connect()

    def _load_conn(self):
        self._command_obj = Command(self)
        if self.is_running:
            self.loop()

        while self.is_running:
            self.stayin_alive()
            self._last_conn_check = time.time()
            time.sleep(320)

    def _assemble_commands(self):
        commands = [cls for cls in self._command_obj.__inheritors__.items()]
        for command in commands:
            self._commands[command.command_name.lower()] = []
            self._commands[command.command_name.lower()].append(
                    command.help_docs)
            self._commands_hooks[command.command_name] = command.callable_hooks
            self._commands_hooks[command.command_name].insert(0, 
                    command.command_name)

    def _process_line(self, line):
        """Processes a single line from IRC. Should be
        overrided."""
        parse = parser.Parser(line, self._nick)
        result = parse._load()
        if not result:
            return
        if self._line_parser:
            self._line_parser(line, parse)
        elif not self._line_parser and self.rc_watch:
            rc.RC(parse)
        else:
            self._process_data(line, parse)
        
    def _process_data(self, line, parse):
        """Processes a single line of data when _line_parser
        is no specified."""
        if parse.is_command:
            if parse.command_name in self._command_hooks[parse.command_name]:
                command = self.get_command_instance(parse.command_name)
                if len(parse.args) < command.req_args:
                    self.say(u"<bold>{0}<normal>, You have not provided "+ \
                            "enough arguments to {1}".format(parse.nick, 
                            parse.command_name), parse.chan)
                elif len(parse.args) > command.req_args:
                    self.say(u"<bold>{0}<normal>, {1} arguments required "+ \
                            "for {2}, {3} given".format(parse.nick,
                            unicode(parse.req_args), len(parse.args)))
                else:
                    command.call(args=parse.args.insert(0, parse), 
                            kwargs=parse.kwargs)
            else:
                return

    def get_command_instance(self, command_name):
        commands = [cls for cls in self._command_obj.__inheritors__.items()]
        for command in commands:
            if command.command_name == command:
                return command
            else:
                continue

    def get_command_hooks(self, command_name):
        for command in self._commands.keys():
            if command == command_name:
                return self.get_command_instance(command).callable_hooks
            else:
                continue

    def get_command_docs(self, command_name):
        for command in self._commands.keys():
            if command == command_name:
                return self.get_command_instance(command).help_docs
            else:
                continue

    def __repr__(self):
        """Reutrn a canonical string representation of IRC."""
        return u"IRC(server=({0!r}, {1!r}), nick={2!r}, realname={3!r}"+ \
                "ident=4!r".format(self._host, unicode(self.port), self._nick,
                self._real_name, self._ident)

    def __str__(self):
        """Return a prettier string representation of IRC."""
        res = u"<IRC ({0!r}, {1!r}) with nickname {2!r} and ident {3!r})>"
        return res.format(self._host, unicode(self._port), self._nick, 
                self._ident)

class Command(object):
    req_args = 0
    command_name = None
    callable_hooks = []
    help_docs = None

    """Tracks inheritence."""
    class __metaclass__(type):
        __inheritors__ = collections.defaultdict(list)

        def __new__(meta, name, bases, dct):
            klass = type.__new__(meta, name, bases, dct)
            for base in klass.mro()[1:-1]:
                meta.__inheritors__[base.__name__].append(klass)
            return klass

    def __init__(self, irc):
        """Base class for all commands."""
        self.say = lambda msg, target: self.irc.say(msg, target)
        self.action = lambda target, msg: self.irc.action(target, msg)
        self.notice = lambda target, msg: self.irc.notice(target, msg)
        self.join = lambda chan: self.irc.join(chan)
        self.part = lambda chan, msg=None: self.irc.part(chan, msg)
        self.mode = lambda t, level, msg: self.irc.mode(target, level, 
                                                        msg)
        self.ping = lambda target: self.irc.ping(target)
        self.setup()

    def setup(self):
        """Attempts to complete any pre-exection tasks
        the command specifies. Runs on initiation. Is
        idle by default; override if necessary."""
        pass

    def call(self, parser, args=None, kwargs=None):
        """Main entry point for the command and the 
        main means by which the task does stuff. Is
        used by other parts of the module to run the
        command when requested via IRC. Should be 
        overrided always."""
        pass

    def __repr__(self):
        """Returns a canonical string representation of Command."""
        return "Command(name={0!r}, hooks={1!r}, help={2!r}".format(
                self.command_name, self.callable_hooks, self.help_docs)

    def __str__(self):
        """Returns a prettier string representation of COmmand."""
        return "<Command {0}>".format(self.command_name)

if __name__ == '__main__':
    irc = IRC()
    irc._load_conn()
