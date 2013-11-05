"""Main entry point for API server."""

import tornado.ioloop
import tornado.web
import sys
import base64


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
            if user != "demo" or passwd != "demo":
                raise ValueError("Invalid username or password")
        except ValueError as e:
            msg = "Authorization failed: {}".format(e)
            raise tornado.web.HTTPError(401, msg)
        else:
            return user

    def write_error(self, status_code, **kwargs):
        # if unauthorized, tell client that authorization is required
        if status_code == 401:
            self.set_header('WWW-Authenticate', 'Basic realm=Restricted')
        # use default errors
        super(APIRequestHandler, self).write_error(status_code, **kwargs)


class MainHandler(APIRequestHandler):

    def get(self):
        username = self.require_auth()
        self.write("Hello, {}.".format(username))


if __name__ == "__main__":
    application = tornado.web.Application([
        (r"/", MainHandler, dict(auth_provider=None)),
    ])
    application.listen(int(sys.argv[1]))
    tornado.ioloop.IOLoop.instance().start()
