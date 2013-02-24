"""Contains all exceptions Cerabot will need."""

class CerabotBaseError(Exception):
    """Base exception for all follwing exceptions"""

class MissingSettingsError(CerabotBaseError):
    """The settings dictionary in settings.py
    Is empty.
    """

class NoPasswordError(MissingSettingsError):
    """The passwd was not provided and 
    passwd_file is empty.
    """
