"""APIRequestHandler subclasses for API endpoints."""

from bs4 import BeautifulSoup
from tornado.web import HTTPError, asynchronous
from tornado import gen
import pbkdf2
import logging
import yaml
import urlparse

from feedreader.api_request_handler import APIRequestHandler
from feedreader.database import Feed, User

logger = logging.getLogger(__name__)


class MainHandler(APIRequestHandler):

    def get(self):
        """Return a hello world message."""
        with self.get_db_session() as session:
            username = self.require_auth(session)
            self.write({"message": "Hello, {}.".format(username)})


class UsersHandler(APIRequestHandler):

    def get(self):
        """Return information about the current user."""
        with self.get_db_session() as session:
            user = session.query(User).get(self.require_auth(session))
            username = user.username
        self.write({'username': username})
        self.set_status(200)

    def post(self):
        """Create a new user."""
        body = self.require_body_schema({
            "type": "object",
            "properties": {
                "username": {
                    "type": "string",
                    "pattern": "^[^:\s]*$",
                    "maxLength": 32,
                    "minLength": 1
                },
                "password": {
                    "type": "string",
                    "minLength": 1
                },
            },
            "required": ["username", "password"],
        })

        with self.get_db_session() as session:
            # check if username already exists
            if session.query(User).get(body["username"]) is not None:
                raise HTTPError(400, reason="Username already registered")
            # save new user
            password_hash = pbkdf2.crypt(body["password"])
            new_user = User(body["username"], password_hash)
            session.add(new_user)
            session.commit()
        self.set_status(201)


class FeedsHandler(APIRequestHandler):

    def get(self):
        """Return a list of the user's subscribed feeds."""
        feeds = []
        with self.get_db_session() as session:
            user = session.query(User).get(self.require_auth(session))
            for feed in user.subscriptions:
                feeds.append({
                    'id': feed.id,
                    'name': feed.title,
                    'url': feed.site_url,
                    'image_url': feed.image_url,
                    'unreads': user.get_num_unread_entries(feed),
                })
        self.write({'feeds': feeds})
        self.set_status(200)

    @classmethod
    @gen.coroutine
    def subscribe_feed(cls, session, user, celery_poller, tasks, url):
        """Subscribe the user to a feed and return the feed ID.

        Raises HTTPError if the feed at the given url can't be subscribed to.
        """
        # add a new feed if it doesn't exist already
        feed = session.query(Feed).filter(Feed.feed_url == url).first()
        if feed is None:
            res = yield celery_poller.run_task(tasks.fetch_feed, url)
            res = yaml.safe_load(res)
            if "error" in res:
                logger.warning("Failed to fetch new feed: '{}'"
                               .format(res['error']))
                raise HTTPError(400, reason=res['error'])
            feed = res['feed']
            entries = res['entries']
            parsed_url = urlparse.urlparse(url)
            new_url = urlparse.urlunparse([
                parsed_url.scheme,
                parsed_url.netloc,
                parsed_url.path,
                '',
                '',
                ''
            ])
            new_feed = session.query(Feed).filter(
                Feed.feed_url == new_url
            ).first()
            if new_feed is not None:
                url = new_url
            if new_url != url:
                new_res = yield celery_poller.run_task(
                    tasks.fetch_feed,
                    new_url,
                )
                new_res = yaml.safe_load(new_res)
                if "error" in new_res:
                    logger.warning("Failed to fetch new feed: '{}'"
                               .format(new_res['error']))
                    raise HTTPError(400, reason=new_res['error'])
                new_entries = new_res['entries']
                if len(entries) == len(new_entries):
                    # assume they are the same until proven wrong
                    same = True
                    for i in range(len(entries)):
                        if entries[i].title != new_entries[i].title or\
                           entries[i].content != new_entries[i].content or\
                           entries[i].author != new_entries[i].author or\
                           entries[i].guid != new_entries[i].guid:
                            same = False
                            break
                    if same:
                        feed.feed_url = new_url
            # feed url may have resolved to a feed that already exists
            existing_feed = session.query(Feed)\
                    .filter(Feed.feed_url == feed.feed_url).all()
            if len(existing_feed) > 0:
                feed = existing_feed[0]
            else:
                # only add the first entry with a given guid
                # this assumes the first one is the newest
                entries_by_guid = {}
                for entry in res['entries']:
                    if entry.guid not in entries_by_guid:
                        entries_by_guid[entry.guid] = entry
                feed.add_all(entries_by_guid.values())
                session.commit()
        if user.has_subscription(feed):
            raise HTTPError(400, reason="Already subscribed to feed")

        # subscribe the user to the feed
        user.subscribe(feed)
        session.commit()
        raise gen.Return(feed.id)

    @asynchronous
    @gen.coroutine
    def post(self):
        """Subscribe the user to a new feed."""
        body = self.require_body_schema({
            'type': 'object',
            'properties': {
                'url': {'type': 'string'},
            },
            'required': ['url'],
        })
        with self.get_db_session() as session:
            user = session.query(User).get(self.require_auth(session))
            feed_id = yield self.subscribe_feed(session, user,
                                                self.celery_poller, self.tasks,
                                                body['url'])
            # TODO: technically this is supposed to be an absolute URL
            self.set_header("Location", "/feeds/{}".format(feed_id))
        self.set_status(201)


class FeedHandler(APIRequestHandler):

    def get(self, feed_id):
        """Return metadata for a subscribed feed."""
        with self.get_db_session() as session:
            user = session.query(User).get(self.require_auth(session))
            feed = session.query(Feed).get(int(feed_id))

            # Make sure the feed exists
            if feed is None:
                raise HTTPError(404, reason='This feed does not exist')

            # Make sure the user is subscribed to this feed
            if not user.has_subscription(feed):
                raise HTTPError(404, reason='This feed does not exist')

            self.write({
                'id': feed.id,
                'name': feed.title,
                'url': feed.site_url,
                'image_url': feed.image_url,
                'unreads': user.get_num_unread_entries(feed),
            })
        self.set_status(200)

    def delete(self, feed_id):
        with self.get_db_session() as session:
            user = session.query(User).get(self.require_auth(session))
            feed = session.query(Feed).get(int(feed_id))

            # Make sure the feed exists
            if feed is None:
                raise HTTPError(404, reason='This feed does not exist')

            # Make sure the user is subscribed to this feed
            if not user.has_subscription(feed):
                raise HTTPError(404, reason='This feed does not exist')

            user.unsubscribe(feed)
        self.set_status(204)


class FeedEntriesHandler(APIRequestHandler):

    def get(self, feed_id):
        """Return a list of entry IDs for a feed."""
        entry_filter = self.get_argument('filter', None)

        with self.get_db_session() as session:
            user = session.query(User).get(self.require_auth(session))
            feed = session.query(Feed).get(int(feed_id))

            # Make sure the feed exists
            if feed is None:
                raise HTTPError(404, reason='This feed does not exist')

            # Make sure the user is subscribed to this feed
            if not user.has_subscription(feed):
                raise HTTPError(404, reason='This feed does not exist')

            # Make sure the filter keyword is valid
            if entry_filter not in ['read', 'unread', None]:
                raise HTTPError(400, reason='Filter keyboard is not valid')

            # Get feed entries
            entries = feed.get_entries(user, entry_filter)
            self.write({'entries': [entry.id for entry in entries]})
            self.set_status(200)


class EntriesHandler(APIRequestHandler):

    @classmethod
    @gen.coroutine
    def truncate(cls, content, length):
        return BeautifulSoup(content).get_text()[:length]

    @asynchronous
    @gen.coroutine
    def get(self, entry_ids):
        entry_ids = [int(entry_id) for entry_id in entry_ids.split(",")]

        try:
            length = int(self.get_argument('truncate', 0))
        except ValueError:
            raise HTTPError(400, reason="Invalid truncation size.")

        with self.get_db_session() as session:
            user = session.query(User).get(self.require_auth(session))
            entries = user.get_entries(entry_ids)

            if len(entries) != len(entry_ids):
                raise HTTPError(404, "Entry does not exist.")

            entries_json = []
            for entry in entries:
                entry_json = {
                    "id": entry.id,
                    "title": entry.title,
                    "pub-date": entry.date,
                    "read": user.has_read(entry),
                    "author": entry.author,
                    "feed_id": entry.feed_id,
                    "url": entry.url,
                }

                if length:
                    entry_json['content'] = yield self.truncate(entry.content,
                                                                length)
                else:
                    entry_json['content'] = entry.content
                entries_json.append(entry_json)

            self.write({'entries': entries_json})
        self.set_status(200)

    def patch(self, entry_ids):
        entry_ids = [int(entry_id) for entry_id in entry_ids.split(",")]
        body = self.require_body_schema({
            "type": "object",
            "properties": {
                "read": {"type": "boolean"},
            },
            "required": ["read"],
        })

        with self.get_db_session() as session:
            user = session.query(User).get(self.require_auth(session))
            entries = user.get_entries(entry_ids)

            if len(entries) != len(entry_ids):
                raise HTTPError(404, "Entry does not exist.")

            if body["read"]:
                for entry in entries:
                    if not user.has_read(entry):
                        user.read(entry)
            else:
                for entry in entries:
                    if user.has_read(entry):
                        user.unread(entry)
        self.set_status(200)
