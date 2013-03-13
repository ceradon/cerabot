import re
import sys

class RC(object):
    def __init__(self, parser):
        self.diff = None
        self.user = None
        self.flags = None
        self.oldid = None
        self.title = None
        self.parser = parser
        self.comment = u""
        self.msg_type = u""
        self.diff_size = None

        #For log messages.
        self.target = u""
        self.log_type = None

        self.valid_flags = {"!":"patrolled",
                            "N":"new",
                            "M":"minor",
                            "B":"bot",}

        try:
            self._load_edit()
        except Exception:
            try:
                self._load_log()
            except Exception:
                raise Exception("Something went wrong! We we're "+ \
                        "unable to parse this line.")

    def _load_edit(self):
        line = self.parser.msg
        self.title = line[line.index("[["):line.index("]]")][2:]
        line = line.replace("[[{0}]]".format(self.title), "")
        line = line.strip().split(" ")
        if line[0].strip("02").startswith("http://"):
            x = re.findall("(\d+)?http://en.wikipedia.org/w/index.php"+ \
                    "?diff\=(.*?)&oldid\=(.*?)", line[0])
            self.diff, self.oldid = x[0][1:]
        elif line[0][0] in self.valid_flags.keys():
            self.flags = line[0]
            x = re.findall("(\d+)?http://en.wikipedia.org/w/index.php"+ \
                    "?diff=(.*?)&oldid=(.*?)", line[1])
            self.diff, self.oldid = x[0][1:]
        x = [i for i, x in enumerate(line) if x == "*"]
        self.user = line[x[0]:[1]]
        self.diff_size = line[x[1]+1].strip("(").strip(")")
        self.comment = " ".join(line[x[1]+2:])
        self.msg_type = u"edit"

    def _load_log(self):
        line = self.parser.msg
        line = line.split(" ")
        self.log_type = line[0].strip("[[Special:Log/").strip("]]"), line[1]
        self.target = line[3]
        self.comment = " ".join(line[6:])
        self.msg_type = u"log"

    """Allow easier access to some of the message's
    attributes."""
    @property
    def title(self):
        return self.title

    @property
    def diff(self):
        return self.diff

    @property
    def oldid(self):
        return self.oldid

    @property
    def flags(self):
        if self.flags:
            return self.flags
        else:
            return None

    @property
    def user(self):
        return self.user

    @property
    def size(self):
        return self.diff_size

    @property
    def comment(self):
        return self.comment
