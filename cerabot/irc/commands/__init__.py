class Command(object):
    name = None
    hooks = []
    help_docs = None

    def __init__(self, bot):
        """Base class for all commands."""
        self._bot = bot

        self.say = lambda msg, target: self._bot.irc.say(msg, target)
        self.action = lambda target, msg: self._bot.irc.action(target, msg)
        self.notice = lambda target, msg: self._bot.irc.notice(target, msg)
        self.join = lambda chan: self._bot.irc.join(chan)
        self.part = lambda chan, msg=None: self._bot.irc.part(chan, msg)
        self.mode = lambda t, level, msg: self._bot.irc.mode(target, level, 
                                                        msg)
        self.ping = lambda target: self._bot.irc.ping(target)
        self.reply = lambda msg, data: self._bot.irc.reply(msg, data)
        self.setup()

    def setup(self):
        """Attempts to complete any pre-exection tasks
        the command specifies. Runs on initiation. Is
        idle by default; override if necessary."""
        pass

    def assert_command(self, data):
        """Checks if the current command should be called as a 
        response to *parse*."""
        if self.hooks:
            return data.is_command and data.command_name in self.hooks
        return data.is_command and data.command_name == self.name

    def call(self, data, args=None, kwargs=None):
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
