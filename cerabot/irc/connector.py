import sys
import time
import socket

class Connection(object):
    def __init__(self, nick, passwd, host, port, 
            realname, ident):
        self.host = host
        self.port = port
        self.nick = nick
        self.ident = ident
        self.passwd = passwd
        self.realname = realname
        
        self._last_send = 0
        self._last_pang = 0
        self._last_recvd = time.time()
        
    def connect(self):
        """Connect to the specified IRC server."""
        self.socket = socket.socket(socket.AF_INET, 
                                    socket.SOCK_STREAM)
        try:
            self.socket.connect((self.host, self.port))
            self._send_conn_data()
        except socket.error:
            print "Unable to establish connection; Retrying..."
            print "Sleeping for 10 seconds"
            time.sleep(0)
            self.connect()

    def _send_conn_data(self):
        """Send vital data for our connection."""
        self._send_data("NICK {0}".format(self.nick))
        self._send_data("USER {0} {1} * :{2}".format(
                self.ident, self.host, self.realname))
        if self.passwd:
            self._send("PASS {0}".format(self.passwd))

    def _close_conn(self):
        """Close the connection with the server."""
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except socket.error:
            pass
        self.socket.close()

    def _recieve_data(self, max_size=4096):
        """Recieve data from the server."""
        socket_data = self.socket.recv(max_size)
        if not socket_data:
            #We might have a dead socket, if no data is being returned.
            raise DeadSocketError():
        return socket_data

    def _send_data(self, msg=None):
        """Send data to the server."""
        last_sent = time() - self._last_send
        if last_sent < 0.85:
            time.sleep(0.85 - last_sent)
        try:
            self.socket.sendall(msg + '\r\n')
        except secket.error:
            raise DeadSocketError()
        else:
            self._last_send = time.time()

    def _process_pong(self, line):
        """Processes PONG message from the server."""
        self._last_recvd = time.time()
        if line[0] == "PING":
            self.send_data("PONG {0}".format(line[1][1:])

    def quit(self, msg=None):
        """Quits from the server, but doesn't close connection."""
        if msg:
            self.send_data("QUIT: {0}".format(msg))
        else:
            self.send_data("QUIT")
