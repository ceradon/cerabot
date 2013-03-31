import re
import sys
from cerabot.irc import irc, rc

pretty_edit = "\u000309<bold>New edit:<normal> {flags} <bold>{user}: [[{article}]]"
pretty_edit += "<normal> Oldid: {oldid}; Diff: {diff} ({size}) {comment}"
pretty_log = "

class Watcher(irc.IRC):
    """Connects to the Wikimedia Foundation's recent
    changes IRC server, then uses `RC` in the rc module
    to parse the data from IRC."""
    def __init__(self, bot):
        self._bot = bot
        self.config = self._bot.config
        self.parse = rc.RC
        super(Watcher, self).__init__(self._bot, rc_watch=True, 
            _line_parser=self.parse_rc_line)

    def start_conn(self):
        """Starts a connection to the recent changes server."""
        self.start_conn()

    def parse_rc_line(self, line, data):
        """Runs an individual line of recent changes data through
        the RC object so it can be parsed."""
        if data.msg_type == "PRIVMSG":
            # If the channel is not in our list of channels,
            # do nothing with it, just in case somebody tries
            #to PM us with false data.
            if not data.chan in self.config["watcher"]["channels"]:
                return

            # Process the line.
            rc_data = self.parse(data)

        elif data.msg_type == "376":
            for chan in self.config["watcher"]["channels"]:
                self.join(chan)
            for chan in self.config["watcher"]["report_chans"]:
                self.join(chan)

        self.handle_rc_event(data)

    def handle_rc_event(self, data):
        """Handles an individual line from the recent changes server."""
        if data.msg_type == "edit":
            if "N" in flags:
                event = "page"
            else:
                event = "edit"
                if "B" in flags:
                    event = "bot edit"
                if "M" in flags:
                    event = "minor " + event

        for chan in self._channels:
            if chan in self.config["watcher"]["report_chans"]
