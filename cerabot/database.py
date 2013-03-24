import re
import sys
import oursql
from os import path
from cerabot import exceptions

class Database(object):
    """Database manager for Cerabot. Loads a database
    connection, also contains several functions to ease
    access/modification of databases."""

    def __init__(self, bot, db_name, host=None, port=None,
            user=None, passwd=None):
        self._bot = bot
        self._logger = self._bot.logger
        self._config = self._bot.config["sql"]
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
        if not self._passwd:
            self._passwd = self.read_password_from_default_file()
        database = oursql.connect
        with database(self._host, self._user, self._passwd, 
                self._port) as conn:
            self._connection = conn
            self._cursor = conn.cursor()
            self._is_connected = True
        return

    def _query(self, query, params=()):
        """Queries the database if we are connected."""
        if self.is_connected:
            with self._connection:
                try:
                    self._cursor.execute(query, params=params)
                except oursql.ProgrammingError as e:
                    msg = "Query could not be completed. Got back: {0}"
                    self._logger.exception(msg.format(e))
                    return False
        return True

    def select(self, table, where=None, generator=False, *args):
        """Selects data from *table* in the database we have connected
        to, with arguments *args*."""
        results = []
        statement = "SELECT {0} FROM {1}".format(tuple(args), table)
        if where:
            try:
                statement += "WHERE {0} = {1}".format(where[0], where[1])
            except IndexError:
                raise exceptions.SQLError("`where` must be a tuple or list")
        query = self._query(statement.replace("'", ""))
        if not query:
            raise exceptions.SQLError("`SELECT` query could not be completed.")
        while True:
            results.append(self._cursor.fetchone())
        if generator:
            return (i for i in results)
        else:
            return results

    def insert(self, table, values, specify):
        """Inserts *values* into *table*."""
        strt, end = "INSERT INTO {0} {1}", "VALUES {0}"
        strt = strt.format(table, tuple(specify))
        end = end.format(tuple(values))
        statement = strt + end
        query = self._query(statement.replace("'", ""))
        if not query:
            raise exceptions.SQLError("`INSERT` query could not be completed.")
        return

    def read_password_from_default_file(self):
        """Reads the password to the database from a .my.cnf file."""
        i = open(path.join(path.expanduser("~"), ".my.cnf"), "r")
        content = i.read().strip()
        return re.search("password\=(.*)", content).group(1)

    def shutdown(self):
        """Gracefully shut down all operations."""
        self._connection.close()
        self._cursor.close()
        self._is_connected = True

    @property
    def is_connected(self):
        """Whether or not we are connected to a database."""
        return self._is_connected

    def __repr__(self):
        """Return a canonical string representation of Database."""
        res = "Database(bot={0}, config={1}, database name={2})"
        return res.format(self._bot, self._config, self._db_name)

    def __str__(self):
        """Return a prettier string representation of Database."""
        res = "<Database(bot {0} with config {1}; connected to database {2})>"
        return res.format(self._bot, self._config, self._db_name)
