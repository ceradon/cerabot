import sys
from cerabot import bot

class BotRequestNotifier(bot.Bot):
    """Notifies bot owners of their failed/
    successful request for bot approval.
    """
    name = "bot_request_notifier"
    task = 2

    def __init__(self):
        super(BotRequestNotifier).__init()

    class RCEvent(rc_watcher.RCWatcher):
        def __init__(self):
            super(RCEvent, self).__init__()

        def _handle_line(self, rc_event):
            """Handles a single line on IRC."""
            raise NotImplementedError()

if __name__ == '__main__':
    task = BotRequestNotifier()
    task.run()
