"""Functional tests for the API."""

from tornado.testing import AsyncHTTPTestCase
import base64
import json

import feedreader.main
from feedreader.database import models


TEST_USER = "username1"
TEST_PASSWORD = "password1"


def get_basic_auth(user, passwd):
    """Return basic auth header."""
    return "Basic " + base64.b64encode("{}:{}".format(user, passwd))


def create_user(test_case):
    response = test_case.fetch('/users', method="POST", body=json.dumps(
        {"username": TEST_USER, "password": TEST_PASSWORD})
    )
    test_case.assertEqual(response.code, 201)


class UsersTest(AsyncHTTPTestCase):

    def get_app(self):
        return feedreader.main.get_application()

    def assert_validation_failed(self, response):
        self.assertEqual(response.code, 400)
        self.assertIn("Body input validation failed",
                      json.loads(response.body)["error"]["message"])

    def test_create_new_user(self):
        create_user(self)
        response = self.fetch('/', headers={
            "Authorization": get_basic_auth(TEST_USER, TEST_PASSWORD),
        })
        self.assertEqual(response.code, 200)

    def test_create_new_user_invalid_body(self):
        response = self.fetch('/users', method="POST", body=json.dumps(
            {"username": TEST_USER})
        )
        self.assert_validation_failed(response)

    def test_create_new_user_empty_username(self):
        response = self.fetch('/users', method="POST", body=json.dumps(
            {"username": ""}, {"password": TEST_PASSWORD})
        )
        self.assert_validation_failed(response)

    def test_create_new_user_empty_password(self):
        response = self.fetch('/users', method="POST", body=json.dumps(
            {"username": TEST_USER}, {"password": ""})
        )
        self.assert_validation_failed(response)

    def test_create_duplicate_username(self):
        response = self.fetch('/users', method="POST", body=json.dumps(
            {"username": TEST_USER, "password": TEST_PASSWORD})
        )
        self.assertEqual(response.code, 201)
        response = self.fetch('/users', method="POST", body=json.dumps(
            {"username": TEST_USER, "password": TEST_PASSWORD})
        )
        self.assertEqual(response.code, 400)
        self.assertIn("Username already registered",
                      json.loads(response.body)["error"]["message"])


class FeedsTest(AsyncHTTPTestCase):

    def setUp(self):
        super(FeedsTest, self).setUp()
        create_user(self)
        self.headers = {
            'Authorization': get_basic_auth(TEST_USER, TEST_PASSWORD),
        }

    def get_app(self):
        def hook(Session): self.Session = Session
        return feedreader.main.get_application(db_setup_f=hook)

    def test_get_user_requires_auth(self):
        response = self.fetch('/users/', method='GET')
        self.assertEqual(response.code, 401)

    def test_get_user(self):
        response = self.fetch('/users/', method='GET', headers=self.headers)
        self.assertEqual(response.code, 200)
        self.assertEqual(json.loads(response.body), {
            "username": TEST_USER,
        })

    def test_get_feeds_requires_auth(self):
        response = self.fetch('/feeds/', method='GET')
        self.assertEqual(response.code, 401)

    def test_get_feeds_empty(self):
        response = self.fetch('/feeds/', method='GET', headers=self.headers)
        self.assertEqual(response.code, 200)
        self.assertEqual(json.loads(response.body), {
            "feeds": [],
        })

    def test_get_feeds(self):
        s = self.Session()
        feed1 = models.Feed("Tombuntu", "http://feeds.feedburner.com/Tombuntu",
                            "http://tombuntu.com")
        s.add(feed1)
        s.commit()
        s.add(models.Subscription(TEST_USER, feed1.id))
        s.add(models.Entry(feed1.id, "This is test content.",
                           "http://tombuntu.com/test-content", "Test title",
                           "Tom", 1384402853))
        s.commit()
        response = self.fetch('/feeds/', method='GET', headers=self.headers)
        self.assertEqual(response.code, 200)
        self.assertEqual(json.loads(response.body), {
            "feeds": [
                {
                    "id": feed1.id,
                    "name": feed1.title,
                    "url": feed1.site_url,
                    "unreads": 1,
                },
            ],
        })
        s.close()

    def test_get_feeds_only_shows_subscribed_feeds(self):
        s = self.Session()
        feed1 = models.Feed("Tombuntu", "http://feeds.feedburner.com/Tombuntu",
                            "http://tombuntu.com")
        s.add(feed1)
        s.commit()
        s.add(models.Entry(feed1.id, "This is test content.",
                           "http://tombuntu.com/test-content", "Test title",
                           "Tom", 1384402853))
        s.commit()
        response = self.fetch('/feeds/', method='GET', headers=self.headers)
        self.assertEqual(response.code, 200)
        self.assertEqual(json.loads(response.body), {
            "feeds": [],
        })
        s.close()

    def test_get_feeds_does_not_count_read_entries(self):
        s = self.Session()
        feed1 = models.Feed("Tombuntu", "http://feeds.feedburner.com/Tombuntu",
                            "http://tombuntu.com")
        s.add(feed1)
        s.commit()
        s.add(models.Subscription(TEST_USER, feed1.id))
        entry1 = models.Entry(feed1.id, "This is test content.",
                              "http://tombuntu.com/test-content", "Test title",
                              "Tom", 1384402853)
        s.add(entry1)
        s.commit()
        s.add(models.Read(TEST_USER, entry1.id))
        s.commit()
        response = self.fetch('/feeds/', method='GET', headers=self.headers)
        self.assertEqual(response.code, 200)
        self.assertEqual(json.loads(response.body), {
            "feeds": [
                {
                    "id": feed1.id,
                    "name": feed1.title,
                    "url": feed1.site_url,
                    "unreads": 0,
                },
            ],
        })
        s.close()

    def test_add_feed_requires_auth(self):
        response = self.fetch('/feeds/', method='POST', body=json.dumps({
          'url': 'http://awesome-blog.github.io'
        }))
        self.assertEqual(response.code, 401)

    def test_add_feed_success(self):
        # TODO: mock this so we're not (slowly) fetching a real feed here
        response = self.fetch('/feeds/', method='POST', headers=self.headers,
                              body=json.dumps({
                                  'url': 'http://awesome-blog.github.io'
                              }),
        )
        self.assertEqual(response.code, 201)

    def test_get_feed_entries_feed_does_not_exist(self):
        response = self.fetch('/feeds/1/entries', method='GET',
                              headers=self.headers)
        self.assertEqual(response.code, 404)

    def test_get_feed_entries_requires_auth(self):
        response = self.fetch('/feeds/1/entries', method='GET')
        self.assertEqual(response.code, 401)

    def test_get_feed_entries_all(self):
        s = self.Session()
        feed1 = models.Feed("Tombuntu", "http://feeds.feedburner.com/Tombuntu",
                            "http://tombuntu.com")
        s.add(feed1)
        s.commit()
        s.add(models.Subscription(TEST_USER, feed1.id))
        entry1 = models.Entry(feed1.id, "This is test content.",
                              "http://tombuntu.com/test-content", "Test title",
                              "Tom", 1384402853)
        s.add(entry1)
        s.commit()
        response = self.fetch('/feeds/{}/entries'.format(feed1.id), method='GET',
                              headers=self.headers)
        self.assertEqual(response.code, 200)
        self.assertEqual(json.loads(response.body), {
            "entries": [entry1.id],
        })

    def test_get_feed_entries_unread(self):
        s = self.Session()
        feed1 = models.Feed("Tombuntu", "http://feeds.feedburner.com/Tombuntu",
                            "http://tombuntu.com")
        s.add(feed1)
        s.commit()
        s.add(models.Subscription(TEST_USER, feed1.id))
        entry1 = models.Entry(feed1.id, "This is test content.",
                              "http://tombuntu.com/test-content", "Test title",
                              "Tom", 1384402853)
        entry2 = models.Entry(feed1.id, "This is test content.",
                              "http://tombuntu.com/test-content", "Test title",
                              "Tom", 1384402853)
        s.add(entry1)
        s.add(entry2)
        s.commit()
        s.add(models.Read(TEST_USER, entry1.id))
        s.commit()
        response = self.fetch(
            '/feeds/{}/entries?filter=unread'.format(feed1.id), method='GET',
            headers=self.headers
        )
        self.assertEqual(response.code, 200)
        self.assertEqual(json.loads(response.body), {
            "entries": [entry2.id],
        })

    def test_get_feed_entries_read(self):
        s = self.Session()
        feed1 = models.Feed("Tombuntu", "http://feeds.feedburner.com/Tombuntu",
                            "http://tombuntu.com")
        s.add(feed1)
        s.commit()
        s.add(models.Subscription(TEST_USER, feed1.id))
        entry1 = models.Entry(feed1.id, "This is test content.",
                              "http://tombuntu.com/test-content", "Test title",
                              "Tom", 1384402853)
        entry2 = models.Entry(feed1.id, "This is test content.",
                              "http://tombuntu.com/test-content", "Test title",
                              "Tom", 1384402853)
        s.add(entry1)
        s.add(entry2)
        s.commit()
        s.add(models.Read(TEST_USER, entry1.id))
        s.commit()
        response = self.fetch(
            '/feeds/{}/entries?filter=read'.format(feed1.id), method='GET',
            headers=self.headers
        )
        self.assertEqual(response.code, 200)
        self.assertEqual(json.loads(response.body), {
            "entries": [entry1.id],
        })

    def test_get_feed_entries_invalid_filter(self):
        s = self.Session()
        feed1 = models.Feed("Tombuntu", "http://feeds.feedburner.com/Tombuntu",
                            "http://tombuntu.com")
        s.add(feed1)
        s.commit()
        s.add(models.Subscription(TEST_USER, feed1.id))
        s.commit()
        response = self.fetch(
            '/feeds/{}/entries?filter=foobar'.format(feed1.id), method='GET',
            headers=self.headers
        )
        self.assertEqual(response.code, 400)

    def test_get_entries_requires_auth(self):
        response = self.fetch('/entries/1', method='GET')
        self.assertEqual(response.code, 401)

    def test_get_entries_does_not_exist(self):
        response = self.fetch('/entries/1', method='GET', headers=self.headers)
        # TODO
        #self.assertEqual(response.code, 404)

    def test_get_entries_single(self):
        s = self.Session()
        feed1 = models.Feed("Tombuntu", "http://feeds.feedburner.com/Tombuntu",
                            "http://tombuntu.com")
        s.add(feed1)
        s.commit()
        s.add(models.Subscription(TEST_USER, feed1.id))
        entry1 = models.Entry(feed1.id, "This is test content.",
                              "http://tombuntu.com/test-content", "Test title",
                              "Tom", 1384402853)
        entry2 = models.Entry(feed1.id, "This is test content.",
                              "http://tombuntu.com/test-content", "Test title",
                              "Tom", 1384402853)
        s.add(entry1)
        s.add(entry2)
        s.commit()
        s.add(models.Read(TEST_USER, entry1.id))
        s.commit()
        response = self.fetch('/entries/{}'.format(entry1.id), method='GET',
                              headers=self.headers)
        self.assertEqual(response.code, 200)
        self.assertEqual(json.loads(response.body), {
            "entries": [
                {
                    "title": entry1.title,
                    "pub-date": entry1.date,
                    # TODO "status": "unread",
                    "status": "TODO",
                    "author": entry1.author,
                    "feed_id": feed1.id,
                    "url": entry1.url,
                    "content": entry1.content,
                },
            ]
        })

    def test_get_entries_multiple(self):
        s = self.Session()
        feed1 = models.Feed("Tombuntu", "http://feeds.feedburner.com/Tombuntu",
                            "http://tombuntu.com")
        s.add(feed1)
        s.commit()
        s.add(models.Subscription(TEST_USER, feed1.id))
        entry1 = models.Entry(feed1.id, "This is test content.",
                              "http://tombuntu.com/test-content", "Test title",
                              "Tom", 1384402853)
        entry2 = models.Entry(feed1.id, "This is test content.",
                              "http://tombuntu.com/test-content", "Test title",
                              "Tom", 1384402853)
        s.add(entry1)
        s.add(entry2)
        s.commit()
        s.add(models.Read(TEST_USER, entry1.id))
        s.commit()
        response = self.fetch('/entries/{},{}'.format(entry1.id, entry2.id),
                              method='GET', headers=self.headers)
        self.assertEqual(response.code, 200)
        self.assertEqual(json.loads(response.body), {
            "entries": [
                {
                    "title": entry1.title,
                    "pub-date": entry1.date,
                    # TODO "status": "unread",
                    "status": "TODO",
                    "author": entry1.author,
                    "feed_id": feed1.id,
                    "url": entry1.url,
                    "content": entry1.content,
                },
                {
                    "title": entry2.title,
                    "pub-date": entry2.date,
                    # TODO "status": "unread",
                    "status": "TODO",
                    "author": entry2.author,
                    "feed_id": feed1.id,
                    "url": entry2.url,
                    "content": entry2.content,
                },
            ]
        })
