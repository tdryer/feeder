from celery import Celery
import logging

from feedreader import stub


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

        if debug:
            # silence warning from pika
            logging.getLogger("pika").setLevel(logging.ERROR)
        else:
            self.app.conf.update(
                BROKER_URL='amqp://guest:guest@localhost:5672//',
                CELERY_ALWAYS_EAGER=False,
                CELERY_RESULT_BACKEND='amqp',
            )

        # register tasks with celery
        self.fetch_feed = self.app.task()(self.fetch_feed)

    # celery tasks

    def fetch_feed(self, feed_url, last_modified=None, etag=None):
        """Fetch and parse the feed at the given URL.

        If the given URL is not a feed, this will attempt to find one.

        Any returned models will be missing foreign keys that don't exist yet
        (like Entry.feed_id if the feed is new).

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
        # TODO: last_modified and etag return values not needed since we have
        # to add them to Feed model anyways?

        #print "Fetching feed {}...".format(feed_url)
        #parsed_feed = feedparser.parse(feed_url)
        #if parsed_feed.bozo:
        #    #raise ValueError("Feed URL could not be loaded.")
        #    pass

        # TODO: implement this for real
        feed = stub.generate_dummy_feed(url=feed_url)
        entries = [stub.generate_dummy_entry(None) for _ in range(10)]

        return {
            "feed_url": feed_url,
            "feed": feed,
            "entries": entries,
            "last_modified": None,
            "etag": None,
        }
