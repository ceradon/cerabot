import sys
from cerabot import bot

class BotRequestNotifier(object):
    """Notifies bot owners of their failed/
    successful request for bot approval.
    """
    name = "bot_request_notifier"
    task = 2
