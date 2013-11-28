"""Main entry point for API server."""

from datetime import timedelta
import logging

from tornado import gen
import pbkdf2
import tornado.ioloop
import tornado.web

from feedreader import database, handlers
from feedreader.celery_poller import CeleryPoller
from feedreader.config import Config
from feedreader.tasks.core import Tasks
from feedreader.updater import Updater


def get_application(config, db_setup_f=None):
    """Return Tornado application instance."""
    # initialize the DB so sessions can be created
    create_session = database.initialize_db(config.database_uri)

    if db_setup_f is not None:
        db_setup_f(create_session)

    # XXX create test user
    session = create_session()
    user = database.User("username", pbkdf2.crypt("password"))
    if not session.query(database.User).filter(
            database.User.username == user.username).count():
        session.add(user)
        session.commit()

    # TODO: make this configurable
    tasks = Tasks(config.amqp_uri)

    celery_poller = CeleryPoller(timedelta(milliseconds=5))

    if config.dummy_data:
        # add some test feeds
        # don't any anything that we aren't ok with hammering with requests
        TEST_FEEDS = [
            'http://feeds.feedburner.com/Tombuntu',
            'https://mtomwing.com/blog/feed',
            'http://awesome-blog.github.io/atom.xml',
            'http://www.reddit.com/r/Android/.rss',
            'http://www.reddit.com/.rss',
            'http://feeds2.feedburner.com/Line25',
            'http://feeds.igvita.com/igvita',
            'https://news.ycombinator.com/rss',
            'http://marissamayr.tumblr.com/rss',
            'http://feeds.feedburner.com/tedblog',
            'http://news.google.com/?output=rss',
            'http://awesome-blog.github.io/atom.xml',
            'http://www.ea.com/rss/news',
            'http://feeds.feedburner.com/TheImgurBlog?format=xml',
            'http://blog.dota2.com/feed/',
            'http://feeds.feedburner.com/jquery/',
            'http://blogs.valvesoftware.com/feed/?cat=6',
            'http://feeds.feedburner.com/youtube/PKJx',
            'https://github.com/blog.atom',
            'http://christianheilmann.com/feed/',
            'http://feeds.feedburner.com/yayQuery',
            'http://feeds.feedburner.com/ImgurGallery?format=xml',
            'http://blog.angularjs.org/atom.xml',
        ]
        for url in TEST_FEEDS:
            @gen.coroutine
            def add_feed():
                # This fails for MySQL once the test data has been added before
                try:
                    yield handlers.FeedsHandler.subscribe_feed(
                        session, user, celery_poller, tasks, url
                    )
                # Ignore exceptions for now
                except:
                    pass
            tornado.ioloop.IOLoop.instance().run_sync(add_feed)

    session.commit()
    session.close()

    CHECK_UPDATE_PERIOD = timedelta(minutes=1)
    UPDATE_PERIOD = timedelta(hours=1)

    if config.periodic_updates:
        # create updater and attach to IOLoop
        updater = Updater(UPDATE_PERIOD, create_session, tasks, celery_poller)
        periodic_callback = tornado.ioloop.PeriodicCallback(
            updater.do_updates, CHECK_UPDATE_PERIOD.total_seconds() * 1000
        )
        periodic_callback.start()

    # create tornado application and listen on the provided port
    default_injections = dict(
        create_session=create_session,
        enable_dummy_data=config.dummy_data,
        tasks=tasks,
        celery_poller=celery_poller,
    )
    return tornado.web.Application([
        (r"^/?$", handlers.MainHandler, default_injections),
        (r"^/users/?$", handlers.UsersHandler, default_injections),
        (r'^/feeds/?$', handlers.FeedsHandler, default_injections),
        (r'^/feeds/(?P<feed_id>[0-9]+)$', handlers.FeedHandler,
         default_injections),
        (r'^/feeds/(?P<feed_id>[0-9]+)/entries/?$',
         handlers.FeedEntriesHandler, default_injections),
        (r'^/entries/(?P<entry_ids>(?:\d+,)*\d+)$', handlers.EntriesHandler,
         default_injections),
    ])


def main():
    """Main entry point for the server."""
    logging.basicConfig(format='[%(levelname)s][%(name)s]: %(message)s')
    logging.getLogger().setLevel(logging.INFO)

    config = Config.from_args()
    get_application(config).listen(config.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
