import sys
from ..connector import Connection

class Command(Connection):
    command_name = None
    callable_hooks = []
    help_docs = None

    def __init__(self):
        """Base class for all commands."""
        self.say = lambda msg, target: self.say(msg, target)
        self.action = lambda target, msg: self.action(target, msg)
        self.notice = lambda target, msg: self.notice(target, msg)
        self.join = lambda chan: self.join(chan)
        self.part = lambda chan, msg=None: self.part(chan, msg)
        self.mode = lambda t, level, msg: self.mode(target, level, 
                                                    msg)
        self.ping = lambda target: self.ping(target)
        self.setup()

    def setup(self):
        """Attempts to complete any pre-exection tasks
        the command specifies. Runs on initiation. Is
        idle by default; override if necessary."""
        pass

    def call(self):
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
