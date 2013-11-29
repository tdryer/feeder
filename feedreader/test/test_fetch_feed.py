# pylint: disable=E1101
import pytest
import httpretty
from os import path
import yaml

from feedreader.tasks.core import Tasks


TEST_DATA_DIR = path.join(path.dirname(__file__), "data")


@pytest.fixture
def tasks():
    return Tasks(amqp_uri='')


def test_connection_refused(tasks):
    # TODO: decorator that does this automatically doesn't work with pytest
    httpretty.enable()
    feed_url = "http://example.com/feed.xml"
    httpretty.register_uri(httpretty.GET, feed_url, status=404)
    res = yaml.safe_load(tasks.fetch_feed.delay(feed_url).get())
    assert "error" in res
    httpretty.disable()
    httpretty.reset()


def test_awesome_blog(tasks):
    httpretty.enable()
    feed_url = "http://example.com/feed.xml"
    feed = open(path.join(TEST_DATA_DIR, "awesome-blog.xml")).read()
    httpretty.register_uri(httpretty.GET, feed_url,
                           body=feed, content_type="application/atom+xml",
                           adding_headers={
                                "ETag": "1337",
                                "Last-Modified": "Tue, 15 Nov 1994 12:45:26 +0000",
                           })
    res = yaml.safe_load(tasks.fetch_feed.delay(feed_url).get())
    assert res["feed"].title == "David Yan's CMPT 376W Blog"
    assert res["feed"].site_url == "http://awesome-blog.github.io/"
    assert res["feed"].feed_url == feed_url
    assert res["feed"].etag == "1337"
    assert res["feed"].last_modified == "Tue, 15 Nov 1994 12:45:26 +0000"
    assert res["feed"].last_refresh_date is not None

    assert res["entries"][0].title == "Return of the OPPO Find 5"
    assert res["entries"][0].url == "http://awesome-blog.github.io/2013/11/20/return-of-the-oppo-find-5.html"
    assert res["entries"][0].author == "David Yan"
    assert res["entries"][0].date == 1384934400
    assert res["entries"][0].content.startswith("<p>Yesterday, ")
    assert res["entries"][0].guid == "57785a2b321c948508451096cb98f23a2a697c01"

    httpretty.disable()
    httpretty.reset()
