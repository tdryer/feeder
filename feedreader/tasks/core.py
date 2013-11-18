from celery import Celery


class Tasks(object):

    def __init__(self, debug=False):
        self.app = Celery()
        self.app.conf.update(
            CELERY_ACCEPT_CONTENT=['json'],
            CELERY_ALWAYS_EAGER=True,
            CELERY_ENABLE_UTC=True,
            CELERY_TASK_SERIALIZER='json',
            CELERY_RESULT_SERIALIZER='json',
            CELERY_TIMEZONE='America/Vancouver',
        )

        if not debug:
            self.app.conf.update(
                BROKER_URL='amqp://guest:guest@novus.mtomwing.com:5673//',
                CELERY_ALWAYS_EAGER=False,
                CELERY_RESULT_BACKEND='amqp',
            )

        # register tasks with celery
        self.fetch_feed = self.app.task()(self.fetch_feed)

    # celery tasks

    def fetch_feed(self, feed_url, last_modified=None, etag=None):
        """Fetch and parse the feed at the given URL.

        If the given URL is not a feed, this will attempt to find one.

        Raises SomeException if an error occurs.

        Returns dict containing:
            - feed_url: canonical url of the feed resource
            - feed: new instance of the Feed model, or None if the feed was
              unmodified
            - entries: list of new instances of the Entry model, or empty list
              if the feed was unmodified
            - last_modified: last modified date, if server provides one
            - etag: etag, if server provides one
        """
        return # TODO
