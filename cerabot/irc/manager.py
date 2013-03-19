from cerabot.manager import Manager

class CommandManager(Manager):
    """Manages commands, checks if commands are 
    being called and calls the if they are."""

    def __init__(self):
