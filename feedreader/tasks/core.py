"""Celery tasks."""

#pylint: disable=E0202

import logging
import yaml
from celery import Celery

from feedreader import database
from feedreader.parsed_feed import (get_parsed_feed, FeedParseError,
                                    FeedNotModifiedError)


logger = logging.getLogger(__name__)


class Tasks(object):

    def __init__(self, amqp_uri=''):
        self.app = Celery()
        self.app.conf.update(
            CELERY_ACCEPT_CONTENT=['json'],
            CELERY_ALWAYS_EAGER=True,
            CELERY_ENABLE_UTC=True,
            CELERY_TASK_SERIALIZER='json',
            CELERY_RESULT_SERIALIZER='json',
            CELERY_TIMEZONE='America/Vancouver',
        )

        if amqp_uri:
            self.app.conf.update(
                BROKER_URL='amqp://{}'.format(amqp_uri),
                CELERY_ALWAYS_EAGER=False,
                CELERY_RESULT_BACKEND='amqp',
            )
        else:
            # silence warning from pika
            logging.getLogger("pika").setLevel(logging.ERROR)

        # register tasks with celery
        self.fetch_feed = self.app.task()(self.fetch_feed)

    # celery tasks

    def fetch_feed(self, feed_url, last_modified=None, etag=None,
                   feed_id=None, find_image_url=True, use_discovery=True):
        """Fetch and parse the feed at the given URL.

        If the given URL is not a feed, this will attempt to find one.

        Any returned models will be missing foreign keys that don't exist yet
        (like Entry.feed_id if the feed is new).

        On success, returns dict containing:
            - feed: new instance of the Feed model, or None if the feed was
              unmodified
            - entries: list of new instances of the Entry model, or empty list
              if the feed was unmodified

        On error, returns dict containing:
            - error: description of the error
        """
        logger.info("Fetch feed task STARTED for '{}'".format(feed_url))

        try:
            feed = get_parsed_feed(
                feed_url, last_modified=last_modified, etag=etag,
                find_image_url=find_image_url, use_discovery=use_discovery
            )
        except FeedParseError as e:
            logger.info("Fetch feed task FAILED for '{}': {}"
                        .format(feed_url, e))
            return yaml.safe_dump({
                "error": str(e),
            })
        except FeedNotModifiedError:
            logger.info("Fetch feed task SUCCEEDED for '{}': not modified"
                        .format(feed_url))
            return yaml.safe_dump({
                "feed": None,
                "entries": [],
            })

        feed_model = database.Feed(
            feed.title, feed.url, feed.link, image_url=feed.image_url,
            etag=feed.etag, last_modified=feed.last_modified,
            last_refresh_date=feed.last_refresh_date, id=feed_id
        )

        entry_models = []
        for entry in feed.entries:
            entry_models.append(database.Entry(entry.content, entry.link,
                                               entry.title, entry.author,
                                               entry.date, entry.guid))

        logger.info("Fetch feed task SUCCEEDED for '{}'".format(feed.url))

        # Serialize manually so tests that run in eager mode cover
        # serialization.
        return yaml.safe_dump({
            "feed": feed_model,
            "entries": entry_models,
        })
