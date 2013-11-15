"""Main entry point for API server."""

import tornado.ioloop
import tornado.web
import sys
import pbkdf2

from feedreader.auth_provider import DummyAuthProvider
from feedreader.database import models
from feedreader import handlers


def get_application(db_setup_f=None):
    """Return Tornado application instance."""
    # initialize the DB so sessions can be created
    create_session = models.initialize_db()

    if db_setup_f is not None:
        db_setup_f(create_session)

    # XXX create test user
    session = create_session()
    session.add(models.User("username", pbkdf2.crypt("password")))
    session.commit()
    session.close()

    # create tornado application and listen on the provided port
    default_injections = dict(create_session=create_session)
    return tornado.web.Application([
        (r"^/?$", handlers.MainHandler, default_injections),
        (r"^/users/?$", handlers.UsersHandler, default_injections),
        (r'^/feeds/?$', handlers.FeedsHandler, default_injections),
        (r'^/feeds/(?P<feed_id>[0-9]+)/entries/?$', handlers.FeedEntriesHandler,
         default_injections),
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
