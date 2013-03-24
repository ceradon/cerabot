import sys
import oursql

class Database(object):
    """Database manager for Cerabot. Loads a database
    connection, also contains several functions to ease
    access/modification of databases."""

    def __init__(self, bot):
        self._bot = bot
        self._config = self._bot.config
