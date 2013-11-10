"""APIRequestHandler subclasses for API endpoints."""

import time

from tornado.web import HTTPError

from feedreader.api_request_handler import APIRequestHandler
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
        self.write({
            'feeds': [{
                'id': 1,
                'name': 'David Yan\'s CMPT 376W Blog',
                'url': 'http://awesome-blog.github.io/',
                'unreads': 1337,
            }, {
                'id': 2,
                'name': 'Michael\'s Blog Posts',
                'url': 'https://mtomwing.com/blog/',
                'unreads': 666,
            }, {
                'id': 3,
                'name': 'Tombuntu',
                'url': 'http://tombuntu.com/',
                'unreads': 69,
            }],
        })
        self.set_status(200)

    def post(self):
        body = self.require_body_schema({
            'type': 'object',
            'properties': {
                'url': {'type': 'string'},
            },
            'required': ['url'],
        })
        self.set_status(201)


class EntriesHandler(APIRequestHandler):

    def get(self, dirty_entry_ids):
        entries = []
        for entry_id in [int(id_) for id_ in dirty_entry_ids.split(',')]:
            entries.append({
                'title': 'My Blog Post {}'.format(entry_id),
                'pub_date': time.time(),
                'status': 'read',
                'feed_id': 1,
                'url': 'https://mtomwing.com/blog/post/week-5-freeseer',
                'content': generate_slipsum_entry(),
            })

        self.write({'entries': entries})
        self.set_status(200)
