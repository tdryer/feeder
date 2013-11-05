from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application
import base64

from feedreader.main import APIRequestHandler


def get_basic_auth(user, passwd):
    return "Basic " + base64.b64encode("{}:{}".format(user, passwd))


class TestHandler(APIRequestHandler):

    def get(self):
        username = self.require_auth()
        self.write("ok")


class AuthorizationTest(AsyncHTTPTestCase):

    def get_app(self):
        return Application([("/", TestHandler, dict(auth_provider=None))])

    def assert_auth_failed(self, response):
        self.assertEqual(response.code, 401)
        self.assertIn("WWW-Authenticate", response.headers)
        self.assertEqual(response.headers["WWW-Authenticate"],
                         "Basic realm=Restricted")

    def test_no_auth(self):
        response = self.fetch('/')
        self.assert_auth_failed(response)

    def test_successfull_auth(self):
        response = self.fetch('/', headers={
            "Authorization": get_basic_auth("demo", "demo"),
        })
        self.assertEqual(response.code, 200)

    def test_invalid_password(self):
        response = self.fetch('/', headers={
            "Authorization": get_basic_auth("demo", "invalid"),
        })
        self.assert_auth_failed(response)

    def test_invalid_username(self):
        response = self.fetch('/', headers={
            "Authorization": get_basic_auth("invalid", "demo"),
        })
        self.assert_auth_failed(response)
