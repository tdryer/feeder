"""Tests for APIRequestHandler."""

from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application
import base64
import json
import pbkdf2

from feedreader import database
from feedreader.api_request_handler import APIRequestHandler


def get_basic_auth(user, passwd, method="Basic"):
    return "{} {}".format(method,
                          base64.b64encode("{}:{}".format(user, passwd)))


def get_application(handler):
    """Return Tornado application with demo user."""
    create_session = database.initialize_db('sqlite://')
    app = Application([("/", handler, dict(create_session=create_session,
                                           tasks=None, celery_poller=None))])
    session = create_session()
    # TODO: better way of creating the demo user
    session.add(database.User("demo", pbkdf2.crypt("demo")))
    session.commit()
    session.close()
    return app


class AuthorizationTestHandler(APIRequestHandler):

    def get(self):
        with self.get_db_session() as session:
            username = self.require_auth(session)
        self.write("ok")


class AuthorizationTest(AsyncHTTPTestCase):

    def get_app(self):
        return get_application(AuthorizationTestHandler)

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

    def test_successfull_auth_xbasic(self):
        response = self.fetch('/', headers={
            "Authorization": get_basic_auth("demo", "demo", method="xBasic"),
        })
        self.assertEqual(response.code, 200)

    def test_failed_auth_xbasic(self):
        response = self.fetch('/', headers={
            "Authorization": get_basic_auth("demo", "invalid", method="xBasic"),
        })
        self.assertEqual(response.code, 401)
        self.assertNotIn("WWW-Authenticate", response.headers)

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


class ValidationTestHandler(APIRequestHandler):

    def post(self):
        body = self.require_body_schema({
            "type": "object",
            "properties": {
                "foo": {"type": "string"},
                "bar": {"type": "integer"},
            },
            "required": ["foo", "bar"],
        })
        self.write("{}/{}".format(body["foo"], body["bar"]))


class ValidationTest(AsyncHTTPTestCase):

    def get_app(self):
        return get_application(ValidationTestHandler)

    def test_success(self):
        response = self.fetch("/", method="POST", body=json.dumps({
            "foo": "baz",
            "bar": 1,
        }))
        self.assertEqual(response.body, "baz/1")

    def test_failure_empty(self):
        response = self.fetch("/", method="POST", body=json.dumps({}))
        self.assertEqual(response.code, 400)
        self.assertIn("Body input validation failed",
                      json.loads(response.body)["error"]["message"])

    def test_failure_invalid_type(self):
        response = self.fetch("/", method="POST", body=json.dumps({
            "foo": "baz",
            "bar": "NaN",
        }))
        self.assertEqual(response.code, 400)
        self.assertIn("Body input validation failed",
                      json.loads(response.body)["error"]["message"])

    def test_failure_missing_property(self):
        response = self.fetch("/", method="POST", body=json.dumps({
            "foo": "baz",
        }))
        self.assertEqual(response.code, 400)
        self.assertIn("Body input validation failed",
                      json.loads(response.body)["error"]["message"])
