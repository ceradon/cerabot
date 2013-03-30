import re
import sys
import logging
import stat

from threading import uniform
from threading import Thread, Lock
from os import path, mkdir
from time import sleep
from .utils import flatten
from cerabot import settings
from cerabot.irc.watcher import Watcher
from cerabot.irc.irc import IRC
from cerabot.wiki.api import Site
from cerabot.database import Database

class Bot(object):
    """Main bot class. Acts as the core of Cerabot. Initiates
    instances of commands and tasks and all the things that they 
    will need."""

    def __init__(self):
        self._config = settings.Settings().settings
        self._component_lock = Lock()
        self.threads = {"general":[], "commands":[], "tasks":[]}

        self._logger = None
        self.watcher = None
        self.irc = None
        self.site = None
        self.keep_running = True

    def start_component(self, name, klass):
        """Starts component *kalss* and fills *name* up with the
        classes instance."""
        if name == "irc":
            self.logger.info("Starting IRC component.")
            component = klass(self)
            setattr(self, "irc", component)
            b = Thread(name="irc:main", target=component.start_conn).start()
            self.threads["general"].append(b)
        elif name == "watcher":
            raise NotImplementedError()

    def stop_component(self, name, msg=None):
        """Stop component *name* if it is a string."""
        return getattr(self, name).shutdown(msg)

    def stop_all_components(self):
        """Stops all running components."""
        if self.irc:
            self.stop_component("irc")
        if self.watcher:
            self.stop_component("watcher")

    def _start_logging_component(self):
        """Starts Cerabot's logger."""
        log_dir = path.join(path.dirname(__file__), "logs")
        logger = logging.getLogger("cerabot")
        logger.handlers = []
        logger.setLevel(logging.DEBUG)
        fmt = "[%(asctime)s %(levelname)s] %(name)s: %(message)s"
        datefmt = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)

        file_handle = lambda f: path.join(log_dir, f)
        handler = logging.FileHandler
        if not path.isdir(log_dir):
            if not path.exists(log_dir):
                mkdir(log_dir, stat.S_IWUSR|stat.S_IRUSR|stat.S_IXUSR)
            else:
                print "log_dir ({0}) exists, but is not a directory:"
                raise Exception()

        main_handler = handler(file_handle("bot.log"))
        error_handler = handler(file_handle("error.log"))
        debug_handler = handler(file_handle("debug.log"))

        main_handler.setLevel(logging.INFO)
        error_handler.setLevel(logging.WARNING)
        debug_handler.setLevel(logging.DEBUG)

        for i in (main_handler, error_handler, debug_handler):
            i.setFormatter(formatter)
            logger.addHandler(i)

        stream = logging.StreamHandler()
        stream.setLevel(logging.INFO)
        stream.setFormatter(formatter)
        logger.addHandler(stream)
        self._logger = logger
        return

    def keep_component_alive(self, name, klass):
        """Keeps *name* alive and running. If it stops, restart it with 
        *klass*"""
        component = getattr(self, name)
        if not component.is_running:
            msg = "Component {0} unexpectedly stopped; restarting"
            self._logger.warn(msg.format(name))
            self.start_component(name, klass)

    def cleanup_threads(self, skip=[]):
        """Cleans up all non-running threads."""
        x = re.compile("command:(.*) \(.*\)")
        skip = skip + ["MainThread", "command:quit"]
        _threads = self.threads["commands"] + self.threads["tasks"]
        for i, thread in enumerate(_threads):
            if not thread.is_alive():
                if thread.name in flatten([x.findall(b) for b in skip]):
                    continue
                del _threads[i]
            else:
                continue
        return

    def get_db(self, db_name):
        """Returns a Database object."""
        klass = Database(self, db_name)
        klass._connect()
        return klass

    def run(self):
        """Starts the bot."""
        self._start_logging_component()
        self._logger.info("Starting Cerabot")
        self.start_component("irc", IRC)
        while self.keep_running:
            with self._component_lock:
                self.keep_component_alive("irc", IRC)
            sleep(5)

    @property
    def is_running(self):
        """Whether or not the bot is running."""
        return self.keep_running

    @property
    def config(self):
        return self._config

    @property
    def logger(self):
        """Returns the currently setup logging component."""
        return self._logger

    def stop(self, msg=None):
        if msg:
            self._logger.info("Stopping bot ({0})".format(msg))
        else:
            self._logger.info("Stopping bot")
        self.stop_all_components()
        if self._logger:
            self._logger.close()
        self.keep_looping = False
        self.cleanup_threads()

    def __repr__(self):
        return "Bot(config={0})".format(self.config)

    def __str__(self):
        return "<Bot(config {0})>".format(self.config)
