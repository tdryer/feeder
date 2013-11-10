"""Functional tests for the API."""

from tornado.testing import AsyncHTTPTestCase
import base64
import json

import feedreader.main


def get_basic_auth(user, passwd):
    """Return basic auth header."""
    return "Basic " + base64.b64encode("{}:{}".format(user, passwd))


class UsersTest(AsyncHTTPTestCase):

    def get_app(self):
        return feedreader.main.get_application()

    def assert_validation_failed(self, response):
        self.assertEqual(response.code, 400)
        self.assertIn("Body input validation failed",
                      json.loads(response.body)["error"]["message"])

    def test_create_new_user(self):
        response = self.fetch('/users', method="POST", body=json.dumps(
            {"username": "foo", "password": "bar"})
        )
        self.assertEqual(response.code, 201)
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
        self.headers = {
            'Authorization': get_basic_auth('foo', 'bar'),
        }

    def get_app(self):
        return feedreader.main.get_application()

    def test_get_feeds_success(self):
        response = self.fetch('/feeds/', method='GET', headers={
            'Authorization': get_basic_auth('foo', 'bar')
        })
        self.assertEqual(response.code, 200)

    def test_add_feed_success(self):
        response = self.fetch('/feeds/', method='POST', headers=self.headers,
                              body=json.dumps({
                                  'url': 'http://awesome-blog.github.io'
                              }),
        )
        self.assertEqual(response.code, 201)
