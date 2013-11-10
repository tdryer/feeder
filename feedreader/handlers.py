"""APIRequestHandler subclasses for API endpoints."""

from lxml import html
from tornado.web import HTTPError
import requests

from feedreader.api_request_handler import APIRequestHandler
from feedreader.database.models import Feed
from feedreader.stub import generate_slipsum_entry


class MainHandler(APIRequestHandler):

    def get(self):
        username = self.require_auth()
        self.write({"message": "Hello world!"})


class UsersHandler(APIRequestHandler):

    def post(self):
        """Create a new user."""
        body = self.require_body_schema({
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "password": {"type": "string"},
            },
            "required": ["username", "password"],
        })
        try:
            self.auth_provider.register(body["username"], body["password"])
        except ValueError as e:
            raise HTTPError(400, reason=e.message)
        self.set_status(201)


class FeedsHandler(APIRequestHandler):

    def get(self):
        feeds = []
        with self.get_session() as session:
            for feed in session.query(Feed).all():
                feeds.append({
                    'id': feed.id,
                    'name': feed.title,
                    'url': feed.site_url,
                    'unreads': 1337,
                })
        self.write({'feeds': feeds})
        self.set_status(200)

    def post(self):
        body = self.require_body_schema({
            'type': 'object',
            'properties': {
                'url': {'type': 'string'},
            },
            'required': ['url'],
        })
        with self.get_session() as session:
            dom = html.fromstring(requests.get(body['url']).content)
            title = dom.cssselect('title')[0].text_content()
            session.add(Feed(title, body['url'], body['url']))
        self.set_status(201)


class EntriesHandler(APIRequestHandler):

    def get(self, dirty_entry_ids):
        entries = [generate_slipsum_entry() for _ in dirty_entry_ids.split(',')]
        self.write({'entries': entries})
        self.set_status(200)
