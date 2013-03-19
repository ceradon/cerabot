from .. import *

class Command(object):
    req_args = 0
    command_name = None
    callable_hooks = []
    help_docs = None

    def __init__(self, irc):
        """Base class for all commands."""
        self.irc = irc

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
        """Returns a prettier string representation of Command."""
        return "<Command {0}>".format(self.command_name)
