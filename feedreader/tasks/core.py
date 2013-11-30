"""Celery tasks."""

#pylint: disable=E0202

import calendar
import hashlib
import logging
import time
import yaml
from celery import Celery

import feedparser
from feedreader import database


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
                   feed_id=None):
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

        TODO:
            disallow local URLs
            use etag and last-modified if provided
            check content types and escape html if necessary
            check the http status code
        """

        logger.info("Fetch feed task STARTED for '{}'".format(feed_url))

        # explicit URL denial
        if feed_url in {
            "http://cmpt470.csil.sfu.ca:8004/.*?|cmpt470.csil.sfu.ca:8004/.*?",
        }:
            return yaml.safe_dump({
                "error": "Target URL is forbidden",
            })

        parsed_feed = get_parsed_feed(feed_url)
        if not is_valid(parsed_feed):
            discovered_feed_url = discover_feed(parsed_feed)
            if discovered_feed_url is not None:
                discovered_parsed_feed = get_parsed_feed(discovered_feed_url)
            if (discovered_feed_url is None
                or not is_valid(discovered_parsed_feed)):
                logger.info("Fetch feed task FAILED for '{}'".format(feed_url))
                return yaml.safe_dump({
                    "error": "Failed to fetch feed",
                })
            else:
                feed_url = discovered_feed_url
                parsed_feed = discovered_parsed_feed

        if parsed_feed.status != 200:
            if parsed_feed.status == 301:
                # update feed's feed_url
                pass
            if parsed_feed.status == 410:
                # delete feed from database
                pass

        # parse the feed
        feed_title = parsed_feed.feed.get("title", "Untitled")
        feed_link = parsed_feed.feed.get("link", None)
        etag = parsed_feed.get("etag", None)
        last_modified = parsed_feed.get("modified", None)
        last_refresh_date = int(time.time())
        feed = database.Feed(feed_title, feed_url, feed_link, etag=etag,
                             last_modified=last_modified,
                             last_refresh_date=last_refresh_date)
        feed.id = feed_id

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
            guid = hashlib.sha1(
                entry.get("id", title).encode('utf-8')
            ).hexdigest()
            entry = database.Entry(content, link, title, author, date, guid)
            entries.append(entry)

        logger.info("Fetch feed task SUCCEEDED for '{}'".format(feed_url))

        # Serialize manually so tests that run in eager mode cover
        # serialization.
        return yaml.safe_dump({
            "feed": feed,
            "entries": entries,
        })

# helpers

# link type attribute values that indicate a feed
FEED_MIME_TYPES = [
    'application/rss+xml',
    'application/atom+xml',
]


def get_parsed_feed(feed_url):
    """Return parsed feed from feedparser."""
    parsed_feed = feedparser.parse(feed_url)
    if parsed_feed.bozo:
        logger.warning("Feed '{}' set the bozo bit: '{}'"
                       .format(feed_url, parsed_feed.bozo_exception))
    return parsed_feed


def is_valid(parsed_feed):
    """Return True if parsed_feed looks valid."""
    # version can be "" or not an attribute if invalid
    is_valid_ = parsed_feed.get("version", "") != ""
    if is_valid_:
        logger.info("Parsed feed is valid")
    else:
        logger.info("Parsed feed is invalid")
    return is_valid_


def discover_feed(parsed_feed):
    """Attempt to discover a feed.

    Given a result from feedparser that is not a feed, return an associated
    feed URL or return None.

    See: http://www.rssboard.org/rss-autodiscovery
    """
    logger.info("Attempting to discover feed")

    # extract the list of links from feedparser at all costs
    try:
        links = parsed_feed.feed.links
    except AttributeError:
        links = []
    else:
        if not isinstance(links, list):
            links = []

    # find link urls that appear to be feeds
    discovered_feeds = [
        link.href for link in links if
        link.get('rel', None) == "alternate" and
        link.get('type', None) in FEED_MIME_TYPES and
        len(link.get('href', '')) > 0
    ]

    if len(discovered_feeds) > 0:
        url = discovered_feeds[0]
        logger.info("Feed discovery succeeded: '{}'".format(url))
        return url
    else:
        logger.info("Feed discovery failed")
        return None
