"""Contains all exceptions Cerabot will need."""

class CerabotError(Exception):
    """Base exception for all follwing exceptions"""

class MissingSettingsError(CerabotError):
    """The settings dictionary in settings.py
    Is empty.
    """

class NoPasswordError(MissingSettingsError):
    """The `passwd` variablewas not provided 
    and the `passwd_file` variable is empty.
    """

class RunPageDisabledError(CerabotError):
    """The on-wiki page is disabled."""
