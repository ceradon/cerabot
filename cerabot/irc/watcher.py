import re
import sys
from cerabt.irc.irc import IRC
import cerabot.irc.parser as d
from cerabot.irc.rc import RC
from cerabot.irc.connection import Connection

pretty_edit = "\u000309<bold>New {event}:<normal> <bold>{user}: [[{article}]]"
pretty_edit += "<normal> Oldid: {oldid}; Diff: {diff} ({size}) \u000313{url}<normal> {comment}"
pretty_log = "\u000309<bold>New {event}:<normal> <bold>{user}:<normal> {comment}"

class Watcher(Connection):
    """Connects to the Wikimedia Foundation's recent
    changes IRC server, then uses `RC` in the rc module
    to parse the data from IRC."""
    def __init__(self, bot):
        self._bot = bot
        self._logger = self._bot.logger
        self.config = self._bot.config

    def start_conn(self):
        """Starts a connection to the recent changes server."""
        config = self.config["watcher"]
        Connection.__init__(self._logger, config["nick"], None , config["server"][0],
            config["server"][1], config["realname"], config["ident"], False, True)
        self.connect()
        self._connection = IRC(self._bot, rc_watch=True)
        self._connection.connect()
        if self.is_running:
            self.loop()

        while self.is_running:
            self.stayin_alive()
            self._last_conn_check = time.time()
            time.sleep(320)

    def _process_line(self, line):
        """Runs an individual line of recent changes data through
        the RC object so it can be parsed."""
        config = self.config["watcher"]
        data = d.Parser(line, config["nick"])
        data._load()
        if data.msg_type == "PRIVMSG":
            # If the channel is not in our list of channels,
            # do nothing with it, just in case somebody tries
            #to PM us with false data.
            if not data.chan in config["channels"]:
                return

            # Process the line.
            rc_data = RC(data)

            # Handle a line from the recent changes server
            self.handle_rc_event(rc_data, data.chan)

        elif data.msg_type == "376":
            for chan in config["channels"]:
                self.join(chan)
            for chan in config["report_chans"]:
                self._connection.join(chan)

    def _process_rc_event(self, data, chan):
        """Processes an individual line from the recent changes server."""
        if data.msg_type == "edit":
            if "N" in data.flags:
                event = "page"
            else:
                event = "edit"
                if "B" in data.flags:
                    event = "bot edit"
                if "M" in data.flags:
                    event = "minor " + event
            url = "http://{0}.org/wiki/{1}".format(chan[1:], data.title)
            a = pretty_edit.format(event=event, user=data.user, article=data.title,
                oldid=data.oldid, diff=data.diff, size=data.diff_size, url=url, 
                comment=data.comment)
            return a

        if flags == "delete":
            event = "deletion"  
        elif flags == "protect":
            event = "protection"
        elif flags == "create":
            event = "user"
        else:
            event = flags
        a = pretty_log.format(event=event, user=data.user, comment=data.comment)
        return a

    def handle_rc_event(self, data, chan):
        """Handles an individual line from the recent changes server."""
        config = self.config["watcher"]
        message = self._process_rc_event(data, chan)
        for chan in self._connection._channels:
            if chan in config["report_chans"]:
                self._connection.say(message, chan)
            else:
                continue
        return
