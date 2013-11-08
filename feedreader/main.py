"""Main entry point for API server."""

import tornado.ioloop
import tornado.web
import sys
import base64
import json
import jsonschema
import httplib

from feedreader.auth_provider import DummyAuthProvider


class APIRequestHandler(tornado.web.RequestHandler):
    """Base RequestHandler for use by API endpoints."""

    def initialize(self, auth_provider):
        self.auth_provider = auth_provider

    def require_auth(self):
        """Return the authorized user's username.

        If authorization fails, raise HTTPError. This doesn't attempt to
        gracefully handle invalid authentication headers.
        """
        try:
            auth_header = self.request.headers.get("Authorization")
            if auth_header is None:
                raise ValueError("No Authorization header provided")
            auth_type, auth_digest = auth_header.split(" ")
            user, passwd = base64.decodestring(auth_digest).split(":")
            if auth_type != "Basic":
                raise ValueError("Authorization type is not Basic")
            if not self.auth_provider.authenticate(user, passwd):
                raise ValueError("Invalid username or password")
        except ValueError as e:
            msg = "Authorization failed: {}".format(e)
            raise tornado.web.HTTPError(401, msg)
        else:
            return user

    def require_body_schema(self, schema):
        """Return json body of the request.

        Raises 400 if the body does not match the given schema.
        """
        try:
            body_json = json.loads(self.request.body)
            jsonschema.validate(body_json, schema)
            return body_json
        except jsonschema.ValidationError:
            raise tornado.web.HTTPError(400)

    def write_error(self, status_code, **kwargs):
        # if unauthorized, tell client that authorization is required
        if status_code == 401:
            self.set_header('WWW-Authenticate', 'Basic realm=Restricted')

        # return errors in JSON
        json_error = {
            "error": {
                "code": status_code,
                "message": httplib.responses[status_code],
            }
        }
        self.finish(json_error)


class MainHandler(APIRequestHandler):

    def get(self):
        username = self.require_auth()
        self.write({"message": "Hello world!"})


class UsersHandler(APIRequestHandler):

    def post(self):
        """Create a new user."""
        body = self.require_body_schema({
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "password": {"type": "string"},
            },
            "required": ["username", "password"],
        })
        # TODO: handle username already being taken, empty password
        self.auth_provider.register(body["username"], body["password"])
        self.set_status(201)


def get_application():
    """Return Tornado application instance."""
    # create an AuthProvider that lets anyone log in with username/password
    auth_provider = DummyAuthProvider()
    auth_provider.register("username", "password")

    # create tornado application and listen on the provided port
    application = tornado.web.Application([
        (r"^/?$", MainHandler, dict(auth_provider=auth_provider)),
        (r"^/users/?$", UsersHandler, dict(auth_provider=auth_provider)),
    ])
    return application


def main():
    """Main entry point for the server."""
    get_application().listen(int(sys.argv[1]))
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
