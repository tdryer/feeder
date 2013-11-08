"""APIRequestHandler subclasses for API endpoints."""

from feedreader.api_request_handler import APIRequestHandler


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
        # TODO: handle username already being taken, empty password
        self.auth_provider.register(body["username"], body["password"])
        self.set_status(201)
