import sys
import time
import os.path as path
from cerabot import settings
from cerabot import exceptions
from cerabot.irc import parser
from cerabot.irc import command
from cerabot.irc import connection

class IRC(connection.Connection):
    def __init__(self, rc_watch=False):
        """Main frontend component of the IRC module
        for Cerabot. Loads connection, parses and runs
        commands when called, imports all commands."""
        self.settings = settings.Settings().settings
        self._last_conn_check = 0
        self._commands = {}
        self._command_hooks = {}
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
        if rc_watch:
            self._host = self.settings['rc_server'][0]
            self._port = self.settings['rc_server'][1]
            super(IRC, self).__init__(self._nick, self._passwd,
                  self._host, self._port, self._real_name, self._ident,
                  join_startup_chans=False)
        elif not rc_watch:
            self._host = self.settings['irc_server'][0]
            self._port = self.settings['irc_server'][1]
            self._assemble_commands()
            super(IRC, self).__init__(self._nick, self._passwd,
                  self._host, self._port, self._real_name, self._ident)
        self.connect()

    def _load_conn(self):
        if self.is_running:
            self.loop()

        while self.is_running:
            self.stayin_alive()
            self._last_conn_check = time.time()
            time.sleep(320)

    def _assemble_commands(self):
        commands = [cls for cls in command.Command.__inheritors__.items()]
        for command in commands:
            self._commands[command.command_name.lower()] = []
            self._commands[command.command_name.lower()].append(
                    command.help_docs)
            self._commands_hooks[command.command_name] = command.callable_hooks
            self._commands_hooks[command.command_name].insert(0, 
                    command.command_name)

    def _process_line(self, line):
        parse = parser.Parser(line, self._nick)
        result = parse._load()
        if not result:
            return
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

    def get_command_instance(self, command_name):
        commands = [cls for cls in command.Command.__inheritors__.items()]
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

if __name__ == '__main__':
    irc = IRC()
    irc._load_conn()
