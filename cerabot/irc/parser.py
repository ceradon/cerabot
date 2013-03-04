import re
import sys
from cerabot import settings
from cerabot import exceptions
from cerabot.irc.connector import Connection

class Parser(Connection):
    """Parses a single line from IRC and searches
    for cammands and arguments in that line of 
    data."""

    def __init__(self, line, nick):
        self._line = line
        self._my_name = nick.lower()

        #For commands
        self.args = []
        self.kwargs = {}
        self.triggers = ['!', '.']
        self.is_command = False
        self.command_name = None
        self.private_message = False
        
        #Properties of the line that are 
        #to be loaded
        self.msg = u""
        self.nick = None
        self.host = None
        self.chan = None
        self.ident = None
        self.msg_type = None

    def _load(self):
        """Load message's attribute."""
        self._line = self._line.split()

        (self.nick, self.host) = self._line[0].split('@', 2)
        (self.nick, self.ident) = self.nick[1:].split('!')
        self.chan = self._line[2]
        self.msg_type = self._line[1]
        self.msg = line[3:]

    def _parse(self):
        """Parses a line from IRC."""
        if self.msg_type == "PRIVMSG":
            if self.chan.lower() == self.my_name:
                #This is a private message to us
                self.chan = self.nick
                self.private_message = True
            self._load_args()
            self._load_kwargs()

    def _load_args(self):
        """Loads the arguments to a message."""
        self.args = self.msg.strip().split()
        
        try:
            self.command_name = self.args.pop(0)
        except IndexError:
            return
        
        if self.command_name[0] in self.triggers:
            self.is_command = True
            self.trigger = self.command_name[0]
            self.command_name = self.command_name[1:]
        elif re.match(r"{0}\W*?$".format(re.escape(self.my_nick)),
                      self.command, re.U):
            self.is_command = True
            self.trigger = self.my_name
            self.command_name = self.command_name

    def _load_kwargs(self):
        """Parse keyword arguments, if any."""
        for item in self.args:
            try:
                key, value = re.findall(r"^(.*?)\=(.*?)$", item)[0]
            except IndexError:
                continue
            if key and value:
                self.kwargs[key] = value