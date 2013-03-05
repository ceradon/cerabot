import sys
from cerabot.irc import parser
from cerabot.irc import command
from cerabot.irc import connector

class IRC(object):
    def __init__(self):
        """Main frontend component of the IRC module
        for Cerabot. Loads connection, parses and runs
        commands when called, imports all commands."""
        
