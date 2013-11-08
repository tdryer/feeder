import unittest
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application
import base64
import json

import feedreader.main
from feedreader.main import APIRequestHandler
from feedreader.auth_provider import DummyAuthProvider


def get_basic_auth(user, passwd):
    return "Basic " + base64.b64encode("{}:{}".format(user, passwd))


class UsersTest(AsyncHTTPTestCase):

    def get_app(self):
        return feedreader.main.get_application()

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
        self.assertEqual(response.code, 400)
        self.assertIn("Body input validation failed",
                      json.loads(response.body)["error"]["message"])

if __name__ == "__main__":
    unittest.main()
