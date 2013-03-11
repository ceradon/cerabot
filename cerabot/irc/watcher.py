import re
import sys

class Watcher(irc.IRC):
    def __init__(self):
        self.re_color = re.compile("\x03[0-9]{1,2}(,[0-9]{1,2}?)?")
        self.re_rc_edit = re.compile("\A\[\[(.*)?\]\]\s(.*)?\s?(\d+)?"+ \
                "http://en.wikipedia.org/w/index.php\?diff=(.*)&oldid=(.*)"+ \
                "\s+?\*\s(.*)\s\*\s(\(\+\d+\))?\s(.*)\Z")
        self.re_rc_log = re.compile("\A\[\[(.*)?\]\]\s(\w+)?\s\*\s(.*)"+ \
                "\s\*\s\s(.*)\Z")