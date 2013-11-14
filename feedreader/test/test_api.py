"""Functional tests for the API."""

from tornado.testing import AsyncHTTPTestCase
import base64
import json

import feedreader.main
from feedreader.database import models


def get_basic_auth(user, passwd):
    """Return basic auth header."""
    return "Basic " + base64.b64encode("{}:{}".format(user, passwd))


def create_user(test_case):
    response = test_case.fetch('/users', method="POST", body=json.dumps(
        {"username": "foo", "password": "bar"})
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
            "Authorization": get_basic_auth("foo", "bar"),
        })
        self.assertEqual(response.code, 200)

    def test_create_new_user_invalid_body(self):
        response = self.fetch('/users', method="POST", body=json.dumps(
            {"username": "foo"})
        )
        self.assert_validation_failed(response)

    def test_create_new_user_empty_username(self):
        response = self.fetch('/users', method="POST", body=json.dumps(
            {"username": ""}, {"password": "bar"})
        )
        self.assert_validation_failed(response)

    def test_create_new_user_empty_password(self):
        response = self.fetch('/users', method="POST", body=json.dumps(
            {"username": "foo"}, {"password": ""})
        )
        self.assert_validation_failed(response)

    def test_create_duplicate_username(self):
        response = self.fetch('/users', method="POST", body=json.dumps(
            {"username": "foo", "password": "bar"})
        )
        self.assertEqual(response.code, 201)
        response = self.fetch('/users', method="POST", body=json.dumps(
            {"username": "foo", "password": "bar"})
        )
        self.assertEqual(response.code, 400)
        self.assertIn("Username already registered",
                      json.loads(response.body)["error"]["message"])


class FeedsTest(AsyncHTTPTestCase):

    def setUp(self):
        super(FeedsTest, self).setUp()
        create_user(self)
        self.headers = {
            'Authorization': get_basic_auth('foo', 'bar'),
        }

    def get_app(self):
        def hook(Session): self.Session = Session
        return feedreader.main.get_application(db_setup_f=hook)

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
        s.add(models.Subscription("foo", feed1.id))
        s.add(models.Entry(feed1.id, "This is test content.", "Test title",
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
                    "unreads": 1337, # TODO
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


class EntriesTest(AsyncHTTPTestCase):

    def setUp(self):
        super(EntriesTest, self).setUp()
        create_user(self)
        self.headers = {
            'Authorization': get_basic_auth('foo', 'bar'),
        }

    def get_app(self):
        return feedreader.main.get_application()

    def test_get_entries_success(self):
        response = self.fetch('/entries/1234', method='GET', headers=self.headers)
        self.assertEqual(response.code, 200)

        # TODO: Validate against schema instead
        body = json.loads(response.body)
        self.assertIn('entries', body)
        self.assertIsInstance(body['entries'], list)
