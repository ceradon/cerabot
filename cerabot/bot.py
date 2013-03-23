import re
import sys
import logging
import threading

from time import sleep
from .utils import flatten
from cerabot.irc.watcher import Watcher
from cerabot.irc.irc import IRC
from cerabot.wiki.api import Site

class Bot(object):
    """Main bot class. Acts as the core of Cerabot. Initiates
    instances of commands and tasks and all the things that they 
    will need."""

    def __init__(self):
        self._component_lock = threading.Lock()
        self.logger = logging.getLogger("cerabot")
        self.threads = {"general":[], "commands":[], "tasks":[]}

        self.watcher = None
        self.irc = None
        self.site = None
        self.kepp_running = True

    def start_component(self, name, klass):
        """Starts component *kalss* and fills *name8 up with the
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

    def keep_component_alive(self, name, klass):
        """Keeps *name* alive and running. If it stops, restart it with 
        *klass*"""
        component = getattr(self, name)
        if not component.is_running:
            msg = "Component {0} unexpectedly stopped; restarting"
            self.logger.warn(msg.format(name))
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

    def run(self):
        """Starts the bot."""
        self.logger.info("Starting Cerabot")
        self.start_component("irc", IRC)
        while self.keep_running:
            with self._component_lock:
                self.keep_componenet_alive("irc", IRC)
            sleep(5)

    @property
    def is_running(self):
        """Whether or not the bot is running."""
        return self.keep_running

    def stop(self, msg=None):
        if msg:
            self.logger.info("Stopping bot ({0})".format(msg))
        else:
            self.logger.info("stopping bot")
        self.stop_all_components()
        self.keep_looping = False
        self.cleanup_threads()

    def __repr__(self):
        return "Bot()"

    def __str__(self):
        return "<Bot>"
