import sys
import oursql

class Database(object):
    """Database manager for Cerabot. Loads a database
    connection, also contains several functions to ease
    access/modification of databases."""

    def __init__(self, bot, db_name, host=None, port=None,
            user=None, passwd=None):
        self._bot = bot
        self._config = self._bot.config["db"]
        self._db_name = db_name

        self._host = host if host else self._config["host"]
        self._port = port if port else self._config["port"]
        self._user = user if user else self._config["user"]
        password = passwd if passwd else self._config["passwd"]
        self._passwd = password

        self._cursor = None
        self._connection = None

    def _connect(self):
        """Connects to the database."""
        database = oursql.connect
        with database(self._host, self._user, self._passwd, 
                self._port) as conn:
            self._connection = None
            self._cursor = None
        return
