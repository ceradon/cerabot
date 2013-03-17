import sys
import urllib2
import isbn_hyphenate
from cerabot import bot
from cerabot import settings
from urllib import urlencode
from cerabot import exceptions

class ISBN(bot.Bot):
    """Corrects ISBNs and makes them up to par
    with Wikpedia's ISBN guidelines."""
    def __init__(self):
        self._pages = []
        super(ISBN, self.).__init__()

    def validate_isbn(self, isbn):
        """Validates an ISBN using the ISBN 
        Database (http://isbndb.com/)."""
