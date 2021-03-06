from threading import Thread
from os import path
from time import strftime
from cerabot.manager import _Manager
from cerabot.irc.commands import Command

class CommandManager(_Manager):
    """Manages commands, checks if commands are 
    being called and calls the if they are."""

    def __init__(self, bot):
        self._bot = bot
        super(CommandManager, self).__init__(self._bot, "commands", Command)
        dir = path.join(path.dirname(__file__), "commands")
        self._load_directory(dir)

    def _wrap_assert(self, command, data):
        """Tries to assert whether *command* is being called."""
        try:
            return command.assert_command(data)
        except Exception:
            e = "Error asserting command {0}"
            print e.format(command.name)

    def _wrap_call(self, command, data):
        """Calls and command."""
        try:
            command.call(data)
        except Exception:
            e = "Error calling command {0}"
            print e.format(command.name)

    def call(self, hook, data):
        for name, command in self.resources.items():
            if hook in command.hooks and self._wrap_assert(command, data):
                thread = Thread(target=self._wrap_call, args=(command, data))
                start_time = strftime("%b %d %H:%M:%S")
                thread.name = "command:{0} ({1})".format(command.name,
                        start_time)
                thread.daemon = True
                thread.start()
                self._bot.threads["commands"].append(thread)
                return
