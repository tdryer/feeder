import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Updater(object):

    def __init__(self, update_period):
        """Instantiate Updater.

        update_period is a timedelta specifing when a feed is stale.
        """
        self._update_period = update_period

    def do_updates(self):
        """Collect stale feeds and force_update them."""
        logger.info("Collecting stale feeds...")
        # TODO find all feeds in DB with last modfified < now - update_period

    def force_update(self, feed_id):
        """Update a feed regardless of how stale it is."""
        logger.info("Starting update of stale feed {}".format(feed_id))
        # TODO: set the last_update DB field on the feed to now
        # TODO: call the celery task to get the feed

    def _post_feed_update(self, res):
        """Given result from fetch_feed task, update the feed in the DB."""
        logger.info("Updating DB for updated feed {}")
        # TODO: update feed entries in DB
