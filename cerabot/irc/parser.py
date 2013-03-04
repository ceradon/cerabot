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
        self._nick = nick.lower()

        self.args = []
        self.kwargs = {}
        self.private_message = False

    
