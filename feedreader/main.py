"""Main entry point for API server."""

import tornado.ioloop
import tornado.web
import sys

from feedreader.auth_provider import DummyAuthProvider
from feedreader.database import models
from feedreader import handlers


def get_application():
    """Return Tornado application instance."""
    # initialize the DB so sessions can be created
    create_session = models.initialize_db()

    # create an AuthProvider that lets anyone log in with username/password
    auth_provider = DummyAuthProvider()
    auth_provider.register("username", "password")

    # create tornado application and listen on the provided port
    default_injections = dict(auth_provider=auth_provider,
                              create_session=create_session)
    return tornado.web.Application([
        (r"^/?$", handlers.MainHandler, default_injections),
        (r"^/users/?$", handlers.UsersHandler, default_injections),
        (r'^/feeds/?$', handlers.FeedsHandler, default_injections),
        (r'^/entries/((?:[^/]|\d)+)$', handlers.EntriesHandler,
         default_injections),
    ])


def main():
    """Main entry point for the server."""
    port = int(sys.argv[1])
    get_application().listen(port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
