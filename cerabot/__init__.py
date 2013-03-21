__all__ = ["bot", "settings", "exceptions"]

import wikitools.api as api
import wikitools.wiki as wiki
import wikitools.page as page
import wikitools.user as user
import wikitools.wikifile as file
import wikitools.category as category

import bot
import settings
import exceptions
import mwparserfromhell as parser


def flatten(nested):
    """Combines a bunch of lists and/or tuples into one list."""
    unified_list = []
    for item in nested:
        if isinstance(item, (list, tuple)):
            unified_list.extend(flatten(item))
        else:
            unified_list.append(x)
    return unified_list
