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

class DeadSocketError(CerabotError):
    """IRC Socket is dead."""

class APIError(CerabotError):
    """Error when interacting eith the MediaWiki
    API."""

class APILoginError(APIError):
    """Error when logging into the API."""

class NoConfigError(CerabotError):
    """No config exists or config is empty."""

class SQLError(CerabotError):
    """Error performing something related to an 
    SQL query."""
