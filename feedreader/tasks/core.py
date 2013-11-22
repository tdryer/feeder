"""Celery tasks."""

from celery import Celery
import logging
import feedparser
import time
import calendar

from feedreader.database import models


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
            - feed: new instance of the Feed model, or None if the feed was
              unmodified
            - entries: list of new instances of the Entry model, or empty list
              if the feed was unmodified

        TODO:
            add etag and last-modified to the feed model
            save and use etag and last-modified
            save guid and use it for updating feeds
            check content types and escape html if necessary
            check the http status code
        """

        logger.info("Parsing feed '{}'".format(feed_url))

        # download and parse the feed
        parsed_feed = feedparser.parse(feed_url)
        if parsed_feed.bozo:
            logger.warning("Feed '{}' set the bozo bit: '{}'"
                           .format(feed_url, parsed_feed.bozo_exception))

        # check for failure
        if parsed_feed.version == "":
            logger.warning("Cannot determine version of feed '{}'"
                           .format(feed_url))
            raise ValueError("Failed to fetch feed")

        # parse the feed
        feed_title = parsed_feed.feed.get("title", "Untitled")
        feed_link = parsed_feed.feed.get("link", None)
        feed = models.Feed(feed_title, feed_url, feed_link)

        # parse the entries
        entries = []
        for entry in parsed_feed.entries:
            if "content" in entry and len(entry.content) > 0:
                content = entry.content[0].value
            elif "summary" in entry:
                content = entry.description
            else:
                content = ""
            link = entry.get("link", None)
            title = entry.get("title", "Untitled")
            if "author_detail" in entry:
                author = entry.author_detail.name
            elif "author_detail" in parsed_feed.feed:
                author = parsed_feed.feed.author_detail.name
            else:
                author = "Unknown Author"
            if "updated_parsed" in entry:
                date = int(calendar.timegm(entry.updated_parsed))
            elif "published_parsed" in entry:
                date = int(calendar.timegm(entry.published_parsed))
            else:
                date = int(time.time())
            entry = models.Entry(None, content, link, title, author, date)
            entries.append(entry)

        return {
            "feed": feed,
            "entries": entries,
        }
