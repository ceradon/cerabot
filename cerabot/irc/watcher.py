import re
import sys
from cerabot.irc import irc, rc

pretty_edit = "\u000309<bold>New {event}:<normal> <bold>{user}: [[{article}]]"
pretty_edit += "<normal> Oldid: {oldid}; Diff: {diff} ({size}) \u000313{url}<normal> {comment}"
pretty_log = "\u000309<bold>New {event}:<normal> <bold>{user}:<normal> {comment}"

class Watcher(object):
    """Connects to the Wikimedia Foundation's recent
    changes IRC server, then uses `RC` in the rc module
    to parse the data from IRC."""
    def __init__(self, bot):
        self._bot = bot
        self.config = self._bot.config
        self.parse = rc.RC

    def start_conn(self):
        """Starts a connection to the recent changes server."""
        self._main_conn = irc.IRC(self._bot, join_startup_chans=False)
        self._rc_conn = irc.IRC(self._bot, rc_watch=True, 
                _line_parser=self.parser_rc_line)
        self._main_conn.start_conn()
        self._rc_conn.start_conn()

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

            # Handle a line from the recent changes server
            self.handle_rc_event(rc_data, data.chan)

        elif data.msg_type == "376":
            for chan in self.config["watcher"]["channels"]:
                self._rc_conn.join(chan)
            for chan in self.config["watcher"]["report_chans"]:
                self._main_conn.join(chan)

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
        message = self._process_rc_event(data, chan)
        for chan in self._main_conn._channels:
            if chan in self.config["watcher"]["report_chans"]:
                self._main_conn.say(message, chan)
