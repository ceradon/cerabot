"""Contains all exceptions Cerabot will need."""

class CerabotError(Exception):
    """Base exception for all follwing exceptions"""

class MissingSettingsError(CerabotError):
    """The settings dictionary in settings.py
    Is empty.
    """

class NoPasswordError(CerabotError):
    """The `passwd` variable was not provided 
    and the `passwd_file` variable is empty.
    """

class RunPageDisabledError(CerabotError):
    """The on-wiki page is disabled."""

class PageInUseError(CerabotError):
    """This is raised when the template {{in use}}
    is present in a page's text. We should not be 
    editing pages that are in use.
    """
