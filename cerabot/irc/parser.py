import re
import sys
from cerabot import settings
from cerabot import exceptions
from cerabot.irc import connection

class Parser(connection.Connection):
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
        if not type(self._line) == list:
            try:
                self._line = self._line.split()
            except Exception:
                return False
        re_line = re.compile(r"(.*?).freenode.net")
        if re_line.search(self._line[0], re.I):
            return False
        if self._my_name == self._line[0][1:].lower():
            return False
        if self._line[0] == "PING":
            return False
        self.nick, self.ident, self.host = re.findall(":(.*?)!(.*?)@(.*?)",
                self._line[0])[0]
        self.chan = self._line[2]
        self.msg_type = self._line[1]
        self.msg = " ".join(self._line[3:])
        self._parse()
        return True

    def _parse(self):
        """Parses a line from IRC."""
        if self.msg_type == "PRIVMSG":
            if self.chan.lower() == self._my_name:
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
        elif re.match(r"{0}\W*?$".format(re.escape(self._my_name)),
                      self.command_name, re.U):
            self.is_command = True
            self.trigger = self._my_name
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

    def __repr__(self):
        """Return a canonical string representation of Parser."""
        return u"Parser(line=\"{0!r}\", my name={1!r}".format(
                self._line, self._my_name)

    def __str__(self):
        """Return a prettier string representation of Parser."""
        return u"<Parser \"{0!r}\" for {1!r}".format(
                " ".join(self.line), self._my_name)
