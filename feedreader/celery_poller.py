"""Allows running Celery tasks asynchronously using the Tornado IOLoop."""

from tornado import concurrent
from tornado import ioloop
from tornado import stack_context
import logging
import time

logger = logging.getLogger(__name__)


class CeleryPoller(object):

    def __init__(self, poll_freq):
        self._poll_freq = poll_freq
        self._results_callbacks = []

    @concurrent.return_future
    def run_task(self, task, *args, **kwargs):
        callback = kwargs["callback"]
        del kwargs["callback"]

        # Wrap the callback it takes the result and raises exceptions in the
        # correct stack context.
        def result_callback(result): callback(result.get())
        result_callback = stack_context.wrap(result_callback)

        logger.info("Starting task (should be fast)...")
        self._results_callbacks.append((task.delay(*args, **kwargs),
                                        result_callback))
        logger.info("... task started")
        self._poll_tasks()

    def _poll_tasks(self):
        logger.debug("Polling Celery tasks")
        results_callbacks = []
        t = time.time()
        logger.info("Starting task poll (should be fast)...")
        for result, callback in self._results_callbacks:
            if result.ready():
                logger.info("Finished task")
                # Exception should never be raised here or bad things will
                # happen.
                callback(result)
            else:
                logger.debug("Task is still pending")
                results_callbacks.append((result, callback))
        t = time.time() - t
        logger.info("... polled {} task(s) in {}ms"
                    .format(len(self._results_callbacks), int(t * 1000)))
        self._results_callbacks = results_callbacks
        if len(self._results_callbacks) > 0:
            logger.debug("Tasks are still pending, scheduling next poll")
            ioloop.IOLoop.instance().add_timeout(self._poll_freq,
                                                 self._poll_tasks)
        else:
            logger.debug("All tasks are complete, no polling necessary")
