"""Main entry point for API server."""

import tornado.ioloop
import tornado.web
import sys

from feedreader.auth_provider import DummyAuthProvider
from feedreader import handlers


def get_application():
    """Return Tornado application instance."""
    # create an AuthProvider that lets anyone log in with username/password
    auth_provider = DummyAuthProvider()
    auth_provider.register("username", "password")

    # create tornado application and listen on the provided port
    return tornado.web.Application([
        (r"^/?$", handlers.MainHandler,
         dict(auth_provider=auth_provider)),
        (r"^/users/?$", handlers.UsersHandler,
         dict(auth_provider=auth_provider)),
        (r'^/feeds/?$', handlers.FeedsHandler,
         dict(auth_provider=auth_provider)),
    ])


def main():
    """Main entry point for the server."""
    port = int(sys.argv[1])
    get_application().listen(port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
