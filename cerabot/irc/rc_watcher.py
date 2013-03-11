import re
import sys
from cerabot.irc import irc

class RCWatcher(irc.IRC):
    def __init__(self):
        self.re_color = re.compile("\x03[0-9]{1,2}(,[0-9]{1,2}?)?")
        self.re_rc_edit = re.compile("\A\[\[(.*)?\]\]\s(.*)?\s?(\d+)?"+ \
                "http://en.wikipedia.org/w/index.php\?diff=(.*)&oldid=(.*)"+ \
                "\s+?\*\s(.*)\s\*\s(\(\+\d+\))?\s(.*)\Z")
        self.re_rc_log = re.compile("\A\[\[(.*)?\]\]\s(\w+)?\s\*\s(.*)"+ \
                "\s\*\s\s(.*)\Z")
        super(RCWatcher, self).__init__(rc_watch=True)

    def _parse_rc_line(self, parser):
        """Processes a single line from the IRC server."""
        class RC(object):
            def __init__(self, parser):
                self.diff = None
                self.user = None
                self.flags = None
                self.oldid = None
                self.title = u""
                self.comment = u""
                self.msg_type = u""
                
                self._load()

            def _load(self):
                if self.re_rc_edit.search(parser.msg):
                    edit = self.re_color.sub("", parser.msg)
                    edit = self.re_rc_edit.search(edit)
                    self.msg_type = u"edit"
                    self.title = edit.group(0)
                    if edit.group(1):
                        self.flags = edit.group(1)
                    self.diff = edit.group(3)
                    self.oldid = edit.group(4)
                    self.user = edit.group(5)
                    self.comment = edit.group(7)

                elif self.re_rc_log.search(parser.msg):
                    log = self.re_color.sub("", parser.msg)
                    log = self.re_rc_log.search(log)
                    self.msg_type = u"log"
                    self.log_type = log.group(0).replace(
                            "Special:Log/", ""), log.group(1),
                            log.group(2), log.group(3)

        rc_event = self.RC(parser)
        self._handle_line(rc_event)

    def _handle_line(self, rc_event):
        """Handles a single line in IRC."""
        pass
