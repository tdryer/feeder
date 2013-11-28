import logging
import time

from tornado import ioloop

from feedreader import database

logger = logging.getLogger(__name__)


class Updater(object):

    def __init__(self, update_period, create_session_f, tasks, celery_poller):
        """Instantiate Updater.

        update_period is a timedelta specifing when a feed is stale.
        """
        self._update_period = update_period
        self._create_session_f = create_session_f
        self._tasks = tasks
        self._celery_poller = celery_poller

    def do_updates(self):
        """Collect stale feeds and force_update them."""
        logger.info("Collecting stale feeds...")

        session = self._create_session_f()

        stale_date = int(time.time()) - self._update_period.total_seconds()
        stale_feeds = database.Feed.find_last_updated_before(session,
                                                             stale_date)
        logger.info("Found stale feeds: {}".format(stale_feeds))

        for feed in stale_feeds:
            self.force_update(session, feed)

        session.close()

    def force_update(self, session, feed):
        """Update a feed regardless of how stale it is."""
        logger.info("Starting update of stale feed {}".format(feed.id))

        # set the feed to have been updated now
        # do this now so if something goes wrong we don't try again immediately
        feed.last_refresh_date = int(time.time())
        session.commit()

        # TODO: use etag / last-modified
        future = self._celery_poller.run_task(self._tasks.fetch_feed,
                                              feed.feed_url, feed_id=feed.id)
        ioloop.IOLoop.instance().add_future(future, self._post_feed_update)

    def _post_feed_update(self, future):
        """Given result from fetch_feed task, update the feed in the DB."""
        res = future.result()
        feed = res["feed"]
        entries = res["entries"]
        logger.info("Got fetch result for stale feed {}".format(feed.id))

        if len(entries) == 0:
            logger.info("Feed {} has not been modified".format(feed.id))

        session = self._create_session_f()

        for entry in entries:
            # if guid is unique for this feed's entries, this is a new entry
            existing_entry = session.query(database.Entry)\
                                    .filter(database.Entry.feed_id == feed.id)\
                                    .filter(database.Entry.guid == entry.guid)\
                                    .all()
            if len(existing_entry) == 0:
                logger.info("Adding new entry for feed {}".format(feed.id))
                entry.feed_id = feed.id
                session.add(entry)
            else:
                logger.info("Updating entry for feed {}".format(feed.id))
                # TODO: update existing entry

        session.commit()
        session.close()
