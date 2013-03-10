import sys
import time
import socket
from cerabot import exceptions

class Connection(object):
    def __init__(self, nick, passwd, host, port,
            realname, ident, join_startup_chans=True
            no_login=False):
        self.host = host
        self.port = port
        self.nick = nick
        self.ident = ident
        self.passwd = passwd
        self.realname = realname

        self._last_send = 0
        self._last_ping = 0
        self._no_login = no_login
        self._last_recvd = time.time()
        self._join_startup_chans = join_startup_chans
        self.is_running = False

        self._channels = []

    def connect(self):
        """Connect to the specified IRC server."""
        self.is_running = True
        self.socket = socket.socket(socket.AF_INET,
                                    socket.SOCK_STREAM)
        try:
            self.socket.connect((self.host, self.port))
            self._send_conn_data()
        except socket.error:
            print "Unable to establish connection; Retrying..."
            print "Sleeping for 10 seconds"
            time.sleep(10)
            self.connect()

    def _send_conn_data(self):
        """Send vital data for our connection."""
        self._send_data("NICK {0}".format(self.nick))
        self._send_data("USER {0} {1} * :{2}".format(
                self.ident, self.host, self.realname))
        if self.passwd and not self._no_login:
            self._send_data("PASS {0}".format(
                            self.passwd))
        if self._join_startup_chans:
            for chan in self.settings["join_on_startup"]:
                self.join(chan)

    def _close_conn(self):
        """Close the connection with the server."""
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except socket.error:
            pass
        self.socket.close()

    def _recieve_data(self, max_size=512):
        """Recieve data from the server."""
        socket_data = self.socket.recv(max_size)
        if not socket_data:
            #We might have a dead socket, if no data is being returned.
            raise exceptions.DeadSocketError()
        return socket_data

    def _send_data(self, msg=None):
        """Send data to the server."""
        last_sent = time.time() - self._last_send
        if last_sent < 0.85:
            time.sleep(0.85 - last_sent)
        try:
            self.socket.sendall(msg + '\r\n')
        except secket.error:
            raise excpetions.DeadSocketError()
        else:
            self._last_send = time.time()

    def _process_ping(self, line):
        """Processes PING message from the server."""
        self._last_recvd = time.time()
        if line[0] == "PING":
            self._send_data("PONG {0}".format(line[1][1:]))

    def _process_line(self, line):
        """Processes a line from the server.
        To be implemented in subclasses."""
        raise NotImplementedError()

    def quit(self, msg=None):
        """Quits from the server, but doesn't close connection."""
        if msg:
            self._send_data("QUIT: {0}".format(msg))
        else:
            self._send_data("QUIT")

    def normalize(self, string):
        """Normalizes strings to say in IRC."""
        string = string.replace("<bold>", "\u0002").replace("<underline>",
                "\u001").replace("<italics>", "\u0016")
        string = string.replace("<normal>", "\u000F")
        return string

    def loop(self):
        """Connection's main loop."""
        read_buffer = ""
        while True:
            try:
                read_buffer += self._recieve_data()
            except exceptions.DeadSocketError:
                break

            lines = read_buffer.split("\n")
            read_buffer = lines.pop()
            for line in lines:
                line = line.strip().split()
                self._process_ping(line)
                self._process_line(line)

        self._close_conn()

    def stayin_alive(self):
        """'Feel the city breakin' and everybody shakin''
        Keeps the connection alive, and ensures we are
        still connected to the server."""
        now = time.time()
        if now - self._last_recvd > 120:
            if self._last_ping < self._last_recvd:
                print "The servers been still for awhile; Pinging..."
                self.ping(self.host)
            elif now - self._last_ping > 60:
                print "Haven't heard back from the server;"+ \
                        "Shutting down..."
                self._shutdown("Ba-bye.")

    def _split_message(self, msgs, maxlen, maxsplits=5):
        """Split a large message into multiple messages smaller than maxlen.
        Credit goes to Ben Kurtovic (Earwig) for writing this awesome piece
        of code."""
        words = msgs.split(" ")
        splits = 0
        while words and splits < maxsplits:
            splits += 1
            if len(words[0]) > maxlen:
                word = words.pop(0)
                yield word[:maxlen]
                words.insert(0, word[maxlen:])
            else:
                msg = []
                while words and len(" ".join(msg + [words[0]])) <= maxlen:
                    msg.append(words.pop(0))
                yield " ".join(msg)

    def join(self, chan):
        """Joins a channel on the server."""
        self._send_data("JOIN {0}".format(chan))
        self._channels.append(chan)

    def part(self, chan, msg=None):
        """Parts a channel on the server."""
        if msg:
            self._send_data("PART {0} :{1}".format(chan, msg))
        else:
            self._send_data("PART {0}".format(chan))
        try:
            self._channels.remove(chan)
        except ValueError:
            #We're not in that channel.
            pass

    def say(self, msg, target):
        """Sends PRIVMSG `msg` to `target`."""
        for line in self._split_message(msg, 220):
            self._send_data("PRIVMSG {0} :{1}".format(target,
                            self.normalize(msg)))

    def action(self, target, msg):
        """Sends ACTION `msg` to server."""
        self.say("\x01ACTION {0}\x01".format(msg), target)

    def mode(self, target, level, msg):
        """Sends MODE `msg` to server."""
        self._send_data("MODE {0} {1} {2}".format(target, level,
                                                  msg))

    def notice(self, target, msg):
        for line in self._split_message(msg, 220):
            self._send_data("NOTICE {0} :{1}".format(target,
                                                     msg))

    def ping(self, target):
        """Sends a PING message to `target`."""
        self._send_data("PING {0}".format(target))
        self._last_ping = time.time()

    def shutdown(self, msg):
        if msg:
            self.quit(msg)
        else:
            self.quit()
        self.is_running = False
        self._close_conn()

    def __repr__(self):
        """Return the canonical string representation of Connection."""
        return u"Connection(server=({0!r}, {1!r}), realname={2!r})".format(
                self.host, unicode(self.port), self.realname)

    def __str__(self):
        """Return the prettier string representation of Connection."""
        return u"<Connection ({0!r}, {1!r}); Realname {2!r}>".format(
                self.host, unicode(self.port), self.realname)
