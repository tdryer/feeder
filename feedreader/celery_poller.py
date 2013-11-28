"""Allows running Celery tasks asynchronously using the Tornado IOLoop."""

from tornado import concurrent
from tornado import ioloop
from tornado import stack_context
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CeleryPoller(object):

    def __init__(self, poll_freq):
        self._poll_freq = poll_freq
        self._results_callbacks = []

    @concurrent.return_future
    def run_task(self, task, *args, **kwargs):
        logger.info("Running task '{}'".format(task))
        callback = kwargs["callback"]
        del kwargs["callback"]

        # Wrap the callback it takes the result and raises exceptions in the
        # correct stack context.
        def result_callback(result): callback(result.get())
        result_callback = stack_context.wrap(result_callback)

        self._results_callbacks.append((task.delay(*args, **kwargs),
                                        result_callback))
        self._poll_tasks()

    def _poll_tasks(self):
        logger.info("Polling Celery tasks")
        results_callbacks = []
        for result, callback in self._results_callbacks:
            if result.ready():
                logger.info("Task is done")
                # Exception should never be raised here or bad things will
                # happen.
                callback(result)
            else:
                logger.info("Task is still pending")
                results_callbacks.append((result, callback))
        self._results_callbacks = results_callbacks
        if len(self._results_callbacks) > 0:
            logger.info("Tasks are still pending, scheduling next poll")
            ioloop.IOLoop.instance().add_timeout(self._poll_freq,
                                                 self._poll_tasks)
        else:
            logger.info("All tasks are complete, no polling necessary")
