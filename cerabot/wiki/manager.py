import sys
from time import strftime
from os.path import join, dirname
from cerabot.manager import _Manager
from cerabot.wiki.tasks import Task
from threading import Thread

class TaskManager(_Manager):
    """Manages all of Cerabot's tasks. Loads and reloads 
    them when needed, and starts then when ``Bot`` requests
    a task to be started."""

    def __init__(self, bot):
        self._bot = bot
        self._logger = self._bot.logger
        super(TaskManager, self).__init__(self._bot, "tasks", Task)
        dir = join(dirname(__file__), "tasks")
        self._load_directory(dir)

    def _wrap_call(self, task, **kwargs):
        """Run a particular task, catching and logging any errors."""
        try:
            if kwargs:
                task.run(self._bot, **kwargs)
            else:
                task.run(self._bot)
        except Exception as e:
            error = "Task '{0}' threw an exception and had to stop: {1}"
            self._logger.exception(error.format(task.name, e.message))
        else:
            log = "Task '{0}' was completed successfully"
            self._logger.info(log.format(task.name))

    def start(self, task, **kwargs):
        """Starts a particular task, placing the task in a daemon thread
        and returning the thread."""
        msg = "Attempting to start task {0}"
        self._logger.info(msg.format(task_name))

        try:
            taskobj = self.get(task_name)
        except KeyError:
            msg = "Task {0} does not exist."
            self._logger.error(msg.format(task_name))

        thread = Thread(target=self._wrap_call, args=(taskobj,), kwargs=kwargs)
        start = strftime("%b %d %H:%M:%S")
        thread.name = "task:{0} ({1})".format(task.name, start)
        thread.daemon = True
        thread.start()
        return thread
