import re
import sys
import yaml
import stat
import logging
try:
    import bcrypt
except ImportError:
    bcrypt = None
try:
    import Crypto.Cipher.Blowfish as blowfish
except ImportError:
    blowfish = None
from os import path, mkdir, chmod
from hashlib import sha256
from getpass import getpass
from textwrap import fill, wrap
import logging.handlers as handlers
from .ordered import OrderedDumper
from collections import OrderedDict

class Config(object):
    """Makes a config file from command line input."""
    WIDTH = 79
    PROMPT = "\x1b[32m> \x1b[0m"

    def __init__(self):
        self.data = OrderedDict([
            ("metadata", OrderedDict()),
            ("components", OrderedDict()),
            ("wiki", OrderedDict()),
            ("irc", OrderedDict()),
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

    def _encrypt(self, password):
        if self._cipher:
            mod = len(password) % 8
            if mod:
                password = password.ljust(len(password) + (8 - mod), "\x00")
            return self._cipher.encrypt(password).encode("hex")
        else:
            return password

    def _ask_list(self, text):
        print fill(re.sub("\s\s+", " ", self.PROMPT + text), self.WIDTH)
        print "[one item per line; blank line to end]:"
        result = []
        while True:
            line = raw_input(self.PROMPT)
            if line:
                result.append(line)
            else:
                return result

    def make_new(self):
        if self.check():
            raise Exception("Config already exists.")
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
                encryption key acts as a password to unlock your encryted
                nodes): """)
            self._print("Attempting to encrypt your key...", newline=False)
            if bcrypt and blowfish:
                salt = bcrypt.gensalt(12)
                signature = bcrypt.hashpw(key, salt)
                self._cipher = blowfish.new(sha256(key).digest())
            elif not bycrypt or not blowfish:
                print " error!"
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
                self.data["metadata"]["signature"] = signature
                print " done."
        self._print("""A number of componenets within this bot use logging. 
            Logging may be useful in discovering errors and correcting bug. 
            Enabling this module is recommended and could be beneficial.""")
        if self._ask_bool("Enable logging? "):
            self.data["metadata"]["logging"] = True

        self._print("""This bot comprises several components, all running 
            independently of each other. The IRC component connects to an 
            IRC server, like Freenode or EFnet, and can be interacte with 
            by users on the server sending commands to the bot. The IRC
            watcher, a sub-component of the IRC module connects to an recent
            changes server, such as irc.wikimedia.org, and parses each line,
            returning an object with attributes that can be used in "feed"
            channels or as apart of bot tasks.""")
        self.data["components"]["irc"] = self._ask_bool("Enable IRC? ")
        self.data["components"]["watcher"] = self._ask_bool("Enable IRC "+ \
                                                            "watcher? ")

        def wiki(self):
            print
            wmfbot = self._ask_bool("""Will your bot be run on a Wikimedia 
                Foundation wiki (i.e. wikipedia, wikinews, etc.)? """)
            self.data["wiki"]["is_wmf_wiki"] = wmfbot
            if wmfbot:
                sitename = self._ask("""What is the wiki's name (i.e wikipedia, 
                    wikinews, wikitionary) ?""", default="wikipedia")
                language = self._ask("""What is the wiki's language code (i.e. 
                    'en', 'fr', 'commons', etc.""", default="en")
                self.data["wiki"]["wikiname"] = sitename
                self.data["wiki"]["lang_code"] = language
            else:
                url = self._ask("""What is the url of the site (must include
                    the protocol as well - 'http://')? """)
                script_path = self._ask("""What is the script path? (i.e. As 
                default, MediaWiki script paths are '/w/')? """, default="/w/")
                article_path = self._ask("""What is the article path? (i.e. 
                MediaWiki defaults to '/wiki/')? """, default="/wiki/")
                self.data["wiki"]["baseurl"] = url
                self.data["wiki"]["script_path"] = script_path
                self.data["wiki"]["article_path"] = article_path
            username = self._ask("What is your bot's username on the wiki? ")
            password = self._ask_pass("What is your bot's password? ")
            self.data["wiki"]["username"], self.data["wiki"]["username"] = \
                    username, password
            summary = self._ask("""What would you like to appear at the end 
                of your bot's edits (i.e. ([[User:MyAwesomeBot|Bot]]; $1 is
                a wildcard, and is replace with your bot's username)? """)
            use_https = self._ask("""Would you like to use HTTPS when 
                connecting to the wiki? """, default=True)
            maxlag = self._ask("""What is the highest amount of lag in seconds 
                you will allow your bot to edit at? """, default=10)
            wait_time = self._ask("""How much time do you want your bot to 
                wait between API queries? """, default=4)
            self.data["wiki"]["useHTTPS"] = use_https
            self.data["wiki"]["maxlag"] = maxlag
            self.data["wiki"]["wait_time"] = wait_time
            self.data["wiki"]["summary"] = summary
            if wmfbot:
                baseurl = "https://{0}.{1}.org"
                self.data["wiki"]["baseurl"] = baseurl.format(sitename,
                    language)
                self.data["wiki"]["script_path"] = "/w/"
                self.data["wiki"]["article_path"] = "/wiki/"
            self._print("""Having a shutoff page is recommended as it allows
                users on your wiki to shut the bot off should it malfunction,
                without havibg access to the server that runs it.""")
            if self._ask_bool("Enable shutoff page? ", default=True):
                page = self._ask("""What will be the name of the shut off 
                    page (i.e. User:MyAwesomeBot/Shutoff/Task 16; $1 and $2
                    are wildcards, and contain your bot's username and task
                    number, respectively)? """, default="User:$1/Shutoff")
                content = self._ask("""Page content to indicate whether the 
                    bot is *not* shut off? """, default="run")
                self.data["wiki"]["shutoff"] = OrderedDict([("page", page), 
                    ("disabled", content)])
        wiki()

        def irc(self, name):
            if not type(name) is tuple:
                raise
            if name[0] == "irc":
                print
                irc = self.data["irc"]["main"] = OrderedDict()
                msg = """Hostname of the IRC server to connect to without 
                    the leading 'irc://':"""
                irc["host"] = self._ask(msg, "irc.freenode.net")
                irc["port"] = self._ask("IRC port:", 6667)
                irc["nick"] = self._ask("IRC nickname:")
                irc["ident"] = self._ask("IRC ident", irc["nick"].lower())
                irc["realname"] = self._ask("IRC realname:", "Cerabot")
                if self._ask_bool("Should the bot identify to NickServ?"):
                    ns_user = self._ask("NickServ username:", irc["nick"])
                    ns_pass = self._ask_pass("NickServ password:")
                    irc["nickserv_user"] = ns_user
                    irc["nickserv_pass"] = ns_pass
                chans = "Should any particular channels be joined by default?"
                irc["channels"] = self._ask_list(chans)

            elif name[0] == "watcher":
                print
                watcher = self.data["irc"]["watcher"] = OrderedDict()
                if wmfbot:
                    watcher["host"] = "irc.wikimedia.org"
                    watcher["port"] = 6667
                else:
                    question = """Hostname of the recent changes server to 
                        connect to with out the leading 'irc://'"""
                    watcher["host"] = self._ask(question)
                    watcher["port"] = self._ask("Watcher's port:", 6667)
                nick = self._ask("Watcher's nick:", irc.get("nick"))
                ident = self._ask("Watcher's ident:", nick.lower())
                watcher["nick"] = nick
                watcher["ident"] = ident
                realname = self._ask("Watcher's real name")
                question = "Should the bot identify to NickServ?"
                if not wmfbot and self._ask_bool(question):
                    ns_user = self._ask("NickServ username:", watcher["nick"])
                    ns_pass = self._ask("NickServ password:")
                watcher["nickserv_username"] = ns_user
                watcher["nickserv_password"] = ns_pass
                if wmfbot:
                    chan = "#{0}.{1}".format(language, sitename)
                    watcher["channels"] = [chan]
                else:
                    chans = "Should any particular channels be joined by default?"
                    watcher["cahnnels"] = self._ask_list(chans)
        if self.data["components"]["irc"]:
            irc(("irc"))
        elif self.data["components"]["watcher"]:
            irc(("watcher"))
        self._print("""The settings you have entered will now be saved in a file 
            called config.yml within the same directory as this configuration
            helper. YAML comprises a straight-forward format that is easily
            human-readable so any changes to your bot's configuration can easily 
            be made via this file.""")
        self._save()

    def _save(self):
        try:
            open(self.config.path, "w").close()
            chmod(self.config.path, stat.S_IRUSR|stat.S_IWUSR)
        except IOError:
            print "I can't seem to write to the config file:"
            raise
        directory = path.join(path.dirname(__file__), "config.yml")
        with open(directory, "w") as io:
            yaml.dump(self.data, io, OrderedDumper, ident=4, allow_unicode=True,
                default_flow_style=False)

    def _load(self):
        filename = path.join(path.dirname(__file__), "config.yml")
        with open(filename, 'r') as fp:
            try:
                self._data = yaml.load(fp, OrderedLoader)
            except yaml.YAMLError:
                print "Error parsing config file {0}:".format(filename)
                raise

    def _handle_missing_config(self):
        print "Config file is either missing or empty"
        msg = "Would you like to create a config file now? [Y/n] "
        choice = raw_input(msg)
        if choice.lower().startswith("n"):
            raise exceptions.NoConfigError()
        try:
            return Config().make_new()
        except KeyboardInterrupt:
            raise exceptions.NoConfigError()

    def check(self):
        return path.exists(path.join(path.dirname(__file__), "config.yml"))
