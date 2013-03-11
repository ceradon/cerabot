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
        self.re_color = re.compile("\x03[0-9]{1,2}(,[0-9]{1,2}?)?")
        self.re_rc_edit = re.compile("\A\[\[(.*)?\]\]\s(.*)?\s?(\d+)?"+ \
                "http://en.wikipedia.org/w/index.php\?diff=(.*)&oldid=(.*)"+ \
                "\s+?\*\s(.*)\s\*\s(\(\+\d+\))?\s(.*)\Z")
        self.re_rc_log = re.compile("\A\[\[(.*)?\]\]\s(\w+)?\s\*\s(.*)"+ \
                "\s\*\s\s(.*)\Z")
        super(Watcher, self).__init__(rc_watch=True, _line_parser=
                                      self._parse_rc_line)
