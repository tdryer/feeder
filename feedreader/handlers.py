"""APIRequestHandler subclasses for API endpoints."""

from lxml import html
from tornado.web import HTTPError
import requests
import pbkdf2

from feedreader.api_request_handler import APIRequestHandler
from feedreader.database.models import Feed, User, Subscription, Entry


class MainHandler(APIRequestHandler):

    def get(self):
        """Return a hello world message."""
        with self.get_db_session() as session:
            username = self.require_auth(session)
            self.write({"message": "Hello, {}.".format(username)})


class UsersHandler(APIRequestHandler):

    def get(self):
        """Returns details of a user based on their auth string."""
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
                    "maxLength": 32
                },
                "password": {
                    "type": "string"
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
        self.set_status(201)


class FeedsHandler(APIRequestHandler):

    def get(self):
        """Return a list of the user's subscribed feeds."""
        feeds = []
        with self.get_db_session() as session:
            user = session.query(User).get(self.require_auth(session))
            for feed in user.get_feeds(session):
                feeds.append({
                    'id': feed.id,
                    'name': feed.title,
                    'url': feed.site_url,
                    'unreads': user.num_unread_in_feed(session, feed.id),
                })
        self.write({'feeds': feeds})
        self.set_status(200)

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
            username = self.require_auth(session)
            dom = html.fromstring(requests.get(body['url']).content)
            title = dom.cssselect('title')[0].text_content()
            feed = Feed(title, body['url'], body['url'])
            session.add(feed)
            session.commit()
            session.add(Subscription(username, feed.id))
            # TODO: If the feed doesn't already exist, retrive it and add new
            # feed and entries.
            # TODO: Subscribe the user to the feed.
        # TODO: we should indicate the ID of the new feed (location header?)
        self.set_status(201)


class FeedEntriesHandler(APIRequestHandler):

    def get(self, feed_id):
        """Return a list of entry IDs for a feed."""
        with self.get_db_session() as session:
            entry_filter = self.get_argument("filter", None)
            user = session.query(User).get(self.require_auth(session))
            # check if the feed exists and user is subscribed to it
            if user.is_sub_of_feed(session, int(feed_id)):
                entries = user.get_feed_entries(session, feed_id)
                # filter the entries if necessary
                if entry_filter == "read":
                    entry_ids = [
                        entry.id for entry in
                        entries["all_entries"][:entries["num_read"]]
                    ]
                elif entry_filter == "unread":
                    entry_ids = [
                        entry.id for entry in
                        entries["all_entries"][entries["num_read"]:]
                    ]
                elif entry_filter == None:
                    entry_ids = [entry.id for entry in entries["all_entries"]]
                else:
                    self.set_status(400)
                    return
                self.write({'entries': entry_ids})
                self.set_status(200)
            else:
                self.set_status(404)


class EntriesHandler(APIRequestHandler):

    def get(self, entry_ids):
        entry_ids = [int(entry_id) for entry_id in entry_ids.split(",")]
        with self.get_db_session() as session:
            user = self.require_auth(session)
            # TODO: check that the user has permission to see each entry_id
            entries = [session.query(Entry).get(entry_id) for entry_id in
                       entry_ids]
            entries_json = [
                {
                    "title": entry.title,
                    "pub-date": entry.date,
                    "status": "TODO", # TODO
                    "author": entry.author,
                    "feed_id": entry.feed_id,
                    "url": entry.url,
                    "content": entry.content,
                } for entry in entries
            ]
            self.write({'entries': entries_json})
            self.set_status(200)
