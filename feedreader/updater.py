import logging
from datetime import datetime
import time

from feedreader.database import models


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Updater(object):

    def __init__(self, update_period, create_session_f):
        """Instantiate Updater.

        update_period is a timedelta specifing when a feed is stale.
        """
        self._update_period = update_period
        self._create_session_f = create_session_f

    def do_updates(self):
        """Collect stale feeds and force_update them."""
        logger.info("Collecting stale feeds...")

        session = self._create_session_f()

        stale_date = int(time.time()) - self._update_period.total_seconds()
        stale_feeds = models.Feed.find_last_updated_before(session, stale_date)
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

        # TODO: call the celery task to get the feed

    def _post_feed_update(self, res):
        """Given result from fetch_feed task, update the feed in the DB."""
        logger.info("Updating DB for updated feed {}")
        # TODO: update feed entries in DB
