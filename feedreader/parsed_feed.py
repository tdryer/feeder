"""Friendlier wrapper around feedparser.

Adds extra features like feed discovery and image discovery. All attributes
have sensible values: None indicates they are not present in the feed.
"""

import calendar
import cgi
import feedparser
import hashlib
import logging
import requests
import time
import urlparse


LOG = logging.getLogger(__name__)
# link type attribute values that indicate a feed
FEED_MIME_TYPES = [
    'application/rss+xml',
    'application/atom+xml',
]
# content type attributes that indicate feedparser sanitized the content
HTML_MIME_TYPES = [
    'text/html',
    'application/xhtml+xml',
]
# valid schemes for feed URLs
VALID_SCHEMES = ['http', 'https']


class FeedParseError(Exception):
    """Failed to parse feed."""
    pass


class FeedNotModifiedError(Exception):
    """Requested feed but it was not modified."""
    pass


class ParsedFeed(object):
    """Parsed feed."""

    def __init__(self):
        self.entries = []
        self.etag = ""
        self.image_url = ""
        self.last_modified = ""
        self.last_refresh_date = ""
        self.link = ""
        self.title = ""
        self.url = ""


class ParsedEntry(object):
    """Parsed feed entry."""

    def __init__(self):
        self.author = ""
        self.content = ""
        self.date = ""
        self.guid = ""
        self.link = ""
        self.title = ""


def get_parsed_feed(url, find_image_url=False, use_discovery=True,
                    last_modified=None, etag=None):
    """Parse feed from given URL.

    Raises FeedParseError if feed cannot be parsed.
    """
    return _parse_result(*_get_result(
        url, etag=etag, last_modified=last_modified,
        use_discovery=use_discovery,
    ), find_image_url=find_image_url)


###############################################################################
# Private Helpers
###############################################################################


def _get_result(url, etag=None, last_modified=None, use_discovery=False):
    """Return feedparser result for url, optionally with discovery.

    Raises FeedParseError.
    """
    _validate_url(url)

    result = feedparser.parse(url, etag=etag, modified=last_modified)
    # update URL for any redirects that feedparser followed
    url = result.get('href', url)

    if _is_not_modified_result(result):
        raise FeedNotModifiedError
    elif not _is_valid_result(result):
        if use_discovery:
            url = _discover_url(result)
            return _get_result(url)
        else:
            _fail(url, "Failed to download or parse feed")
    else:
        return url, result


def _is_not_modified_result(result):
    """Return True if feedparser result indicates feed was not modified."""
    return result.get('status', None) == 304


def _is_valid_result(result):
    """Return True if feedparser result looks valid."""
    return result.get("version", "") != ""


def _discover_url(result):
    """Attempt to discover a feed url using a feedparser result.

    Raises FeedParseError if url can not be discovered.

    See: http://www.rssboard.org/rss-autodiscovery
    """
    # abuse feedparser result to get link tags from html page
    try:
        links = result.feed.links
    except AttributeError:
        links = []
    if not isinstance(links, list):
        links = []

    # find link urls that appear to be feeds
    discovered_feeds = [
        link.href for link in links if
        link.get('rel', None) == "alternate" and
        link.get('type', None) in FEED_MIME_TYPES and
        len(link.get('href', '')) > 0
    ]

    if len(discovered_feeds) == 0:
        _fail(None, "Failed to download or parse feed")  # XXX

    return discovered_feeds[0]


def _fail(url, reason):
    """Raise FeedParseError and log url and reason."""
    LOG.debug("Failed to parse feed '{}': {}".format(url, reason))
    raise FeedParseError(reason)


def _validate_url(url):
    """Raise FeedParseError if url is not valid."""
    if urlparse.urlparse(url).scheme not in VALID_SCHEMES:
        _fail(url, "Invalid URL")


def _parse_result(url, result, find_image_url=False):
    """Parse feedparser result info ParsedFeed."""
    feed = ParsedFeed()
    feed.url = url  # TODO use feed.id
    feed.title = result.feed.get("title", None)
    feed.link = result.feed.get("link", None)
    feed.etag = result.get("etag", None)
    feed.last_modified = result.get("modified", None)
    feed.last_refresh_date = int(time.time())
    if find_image_url:
        feed.image_url = discover_image(feed.link if feed.link is not None else
                                        feed.url)
    else:
        feed.image_url = None
    feed.entries = [_parse_result_entry(entry) for entry in result.entries]
    return feed


def _parse_result_entry(result):
    """Parse feedparser result entry into ParsedEntry."""
    entry = ParsedEntry()

    if "content" in result and len(result.content) > 0:
        entry.content = result.content[0].value
        # if not html, have to escape
        if result.content[0].type not in HTML_MIME_TYPES:
            entry.content = cgi.escape(entry.content)
    elif "summary_detail" in result:
        entry.content = result.summary_detail.value
        # if not html, have to escape
        if result.summary_detail.type not in HTML_MIME_TYPES:
            entry.content = cgi.escape(entry.content)
    else:
        entry.content = ""
    entry.link = result.get("link", None)
    entry.title = result.get("title", None)
    if "author_detail" in result and "name" in result.author_detail:
        entry.author = result.author_detail.name
    else:
        entry.author = None
    if "updated_parsed" in result and result.updated_parsed is not None:
        entry.date = int(calendar.timegm(result.updated_parsed))
    elif "published_parsed" in result and result.published_parsed is not None:
        entry.date = int(calendar.timegm(result.published_parsed))
    else:
        entry.date = int(time.time())
    # try to find something to use as GUID, or fall back to static string
    guid_content = result.get("id", entry.title)
    if guid_content is None:
        guid_content = "None"
    entry.guid = hashlib.sha1(guid_content.encode('utf-8')).hexdigest()
    return entry


def discover_image(url):
    """Return the URL of an image associated with the given site URL.

    Returns None if not icon is found.
    """
    LOG.info("Attempting to discover image for '{}'"
             .format(url.encode('utf-8')))
    # hacky way to use urlparse to get favicon path
    parsed_url = urlparse.urlparse(url)
    favicon_url = urlparse.urlunparse((parsed_url.scheme, parsed_url.netloc,
                                       "favicon.ico", '', '', ''))
    try:
        response = requests.head(favicon_url)
    except requests.exceptions.RequestException:
        response = None

    if response:
        good_status = response.status_code == 200
        good_content_type = response.headers.get('content-type', '')\
                                            .startswith('image/')
        good_content_size = int(response.headers.get('content-length', 0)) > 0
        if good_status and good_content_type and good_content_size:
            LOG.info("Image found at '{}'".format(url.encode('utf-8')))
            return favicon_url

    LOG.info("No image found")
    return None
