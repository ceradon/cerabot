import re
import sys

class RC(object):
    def __init__(self, data):
        self._diff = None
        self._user = None
        self._flags = None
        self._oldid = None
        self._title = None
        self._data = data
        self._comment = u""
        self._msg_type = u""
        self._diff_size = None

        #For log messages.
        self._target = u""
        self._log_type = None

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
        line = self._data.msg
        self._title = line[line.index("[["):line.index("]]")][2:]
        line = line.replace("[[{0}]]".format(self._title), "")
        line = line.strip().split(" ")
        if line[0].strip("02").startswith("http://"):
            x = re.findall("(\d+)?http://en.wikipedia.org/w/index.php"+ \
                    "?diff\=(.*?)&oldid\=(.*?)", line[0])
            self._diff, self._oldid = x[0][1:]
        elif line[0][0] in self.valid_flags.keys():
            self.flags = line[0]
            x = re.findall("(\d+)?http://en.wikipedia.org/w/index.php"+ \
                    "?diff=(.*?)&oldid=(.*?)", line[1])
            self._diff, self._oldid = x[0][1:]
        x = [i for i, x in enumerate(line) if x == "*"]
        self._user = line[x[0]:[1]]
        self._diff_size = line[x[1]+1].strip("(").strip(")")
        self._comment = " ".join(line[x[1]+2:])
        self._msg_type = u"edit"

    def _load_log(self):
        line = self._data.msg
        line = line.split(" ")
        self._log_type = line[0].strip("[[Special:Log/").strip("]]"), line[1]
        self._target = line[3]
        self._comment = " ".join(line[6:])
        self._msg_type = u"log"

    """Allow easier access to some of the message's
    attributes."""
    @property
    def title(self):
        return self._title

    @property
    def diff(self):
        return self._diff

    @property
    def oldid(self):
        return self._oldid

    @property
    def flags(self):
        if self._flags:
            return self._flags
        else:
            return None

    @property
    def user(self):
        return self._user

    @property
    def size(self):
        return self._diff_size

    @property
    def comment(self):
        return self._comment

    @property
    def target(self):
        return self._target

    @property
    def log_type(self):
        return self._log_type

    @property
    def msg_type(self):
        return self._msg_type
