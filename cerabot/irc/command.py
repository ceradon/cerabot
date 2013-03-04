import sys
from ..connector import Connection

class Command(Connection):
    command_name = None
    callable_hooks = []
    help_docs = None

    def __init__(self):
        """Base class for all commands."""
        self.say = lambda msg, target: self.say(msg, target)
        