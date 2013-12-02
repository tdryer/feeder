import logging
import time
import yaml

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
        logger.debug("Collecting stale feeds...")

        session = self._create_session_f()

        stale_date = int(time.time()) - self._update_period.total_seconds()
        stale_feeds = database.Feed.find_last_updated_before(session,
                                                             stale_date)
        logger.debug("Found stale feeds: {}".format(stale_feeds))

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

        # Fetch feed without url or image discover, using any etag or
        # last-modified headers.
        future = self._celery_poller.run_task(
            self._tasks.fetch_feed, feed.feed_url, feed_id=feed.id,
            etag=feed.etag, last_modified=feed.last_modified,
            find_image_url=False, use_discovery=False
        )
        ioloop.IOLoop.instance().add_future(future, self._post_feed_update)

    def _post_feed_update(self, future):
        """Given result from fetch_feed task, update the feed in the DB."""
        res = yaml.safe_load(future.result())

        if "error" in res:
            logger.warning("Failed to update stale feed: '{}'"
                           .format(res["error"]))
            return

        feed = res["feed"]
        entries = res["entries"]

        if feed is None:
            logger.info("Stale feed has not been modified")
            return
        else:
            logger.info("Got result for stale feed {}".format(feed.id))

        session = self._create_session_f()

        # only add the first entry with a given guid
        # this assumes the first one is the newest
        entries_by_guid = {}
        for entry in entries:
            if entry.guid not in entries_by_guid:
                entries_by_guid[entry.guid] = entry

        for entry in entries_by_guid.values():
            # if guid is unique for this feed's entries, this is a new entry
            existing_entry = session.query(database.Entry)\
                                    .filter(database.Entry.feed_id == feed.id)\
                                    .filter(database.Entry.guid == entry.guid)\
                                    .all()
            if len(existing_entry) == 0:
                logger.info("Adding new entry for stale feed {}"
                            .format(feed.id))
            else:
                logger.info("Updating entry for stale feed {}".format(feed.id))
                # modify the existing entry
                entry.id = existing_entry[0].id

            entry.feed_id = feed.id
            session.merge(entry)

        session.commit()
        session.close()
