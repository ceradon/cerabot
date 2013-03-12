import re
import sys
from cerabot.irc import irc
from cerabot.irc import rc

class Watcher(irc.IRC):
    """Connects to the Wikimedia Foundation's recent
    changes IRC server, then uses `RC` in the rc module
    to parse the data from IRC."""
    def __init__(self):
        self.rc_parser = re.RC
        super(Watcher, self).__init__(rc_watch=True, _line_parser=
                                      self._parse_rc_line)
