import re
import sys
import yaml
try:
    import bcrypt
except ImportError:
    bcrypt = None
try:
    import Crypto.Cipher.Blowfish as blowfish
except ImportError:
    blowfish = None
from hashlib import sha256
from getpass import getpass
from textwrap import fill
from .ordered import OrderedDumper
from collections import OrderedDict

class BuildConfig(object):
    """Makes a config file from command line input."""
    WIDTH = 79
    PROMPT = "\x1b[32m> \x1b[0m"

    def __init__(self):
        self.data = OrderedDict([
            ("metadata", OrderedDict()),
            ("components", OrderedDict()),
            ("wiki", OrderedDict()),
            ("irc", OrderedDict()),
            ("commands", OrderedDict()),
            ("tasks", OrderedDict())
        ])
        self._cipher = None

    def _print(self, text, newline=True):
        if newline:
            print fill(re.sub("\s\s+", " ", text), self.WIDTH)
        else:
            sys.stdout.write(fill(re.sub("\s\s+", " ", text), self.WIDTH))
            sys.stdout.flush()

    def _ask(self, text, default=None, require=True):
        text = self.PROMPT + text
        if default:
            text += " \x1b[33m[{0}]\x1b[0m".format(default)
        lines = wrap(re.sub("\s\s+", " ", text), self.WIDTH)
        if len(lines) > 1:
            print "\n".join(lines[:-1])
        while True:
            answer = raw_input(lines[-1] + " ") or default
            if answer or not require:
                return answer

    def _ask_bool(self, text, default=True):
        text = self.PROMPT + text
        if default:
            text += " \x1b[33m[Y/n]\x1b[0m"
        else:
            text += " \x1b[33m[y/N]\x1b[0m"
        lines = wrap(re.sub("\s\s+", " ", text), self.WIDTH)
        if len(lines) > 1:
            print "\n".join(lines[:-1])
        while True:
            answer = raw_input(lines[-1] + " ").lower()
            if not answer:
                return default
            if answer.startswith("y"):
                return True
            if answer.startswith("n"):
                return False

    def _ask_pass(self, text, encrypt=True):
        password = getpass(self.PROMPT + text + " ")
        if encrypt:
            return self._encrypt(password)
        return password

    def _make_new(self):
        self._print("""Welcome to the bot config helper script. This script
            is here to assist in the creation of a configuration file to make
            the process easier when creating tasks and commands. All input
            you enter will be saved to a file name *config.yml*. The contents
            of the file are human-readable so you will be able to modify the 
            configuration values any time you would like.""")
        self._print("""Before proceeding with filling in the values of the 
            bot's independant components, several general options must be 
            filled in.""")
        self._print("""Data encryption for such values as passwords in 
            recommended. Excrytion of such values helps protect your passwords
            and other sensitive information from being accessed easily. It
            is especially necessary if the bot will be running on public 
            networks, such as the Wikimedia Toolserver, Wikimedia Labs or a
            shell account service. (Note: All data, including passwords, can
            be accessed by the server administrators of these networks, and
            encryption can protect your sensitive data from being accessed 
            easily.""")
        self.data["metadata"]["encryption"] = False
        if self._ask_bool("Encrypt your passwords? "):
            key = getpass(self.PROMPT + """Enter an encryption key (an 
                encryption key is a random string of data, so bam on your
                keyboard a couple and you'll be good!): """)
            if bcrypt and blowfish:
                salt = bcrypt.gensalt(self.BCRYPT_ROUNDS)
                signature = bcrypt.hashpw(key, salt)
                self._cipher = blowfish.new(sha256(key).digest())
            elif not bycrypt or not blowfish:
                self._print("""In order for encryption to take place, you 
                must have the packages 'pycrypto' and 'pybcrypt' to be 
                installed.""")
                strt, end = " * \x1b[36m", "\x1b[0m"
                print start+"http://www.mindrot.org/projects/py-bcrypt/"+end
                print start+"https://www.dlitz.net/software/pycrypto/"+end
                self._print("""Encryption is disabled for now; to enable it
                    install the required packages and edit the config varable
                    *encryption* under *metadata* to True.""")
            else:
                self.data["metadata"]["encryption"] = True
                self.data["metadata"]["signature"] = key
                print " done."
