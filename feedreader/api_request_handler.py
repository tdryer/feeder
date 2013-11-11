from contextlib import contextmanager
import base64
import httplib
import json
import jsonschema
import tornado.web
import pbkdf2

from feedreader.database import models


class APIRequestHandler(tornado.web.RequestHandler):
    """Base RequestHandler for use by API endpoints."""

    def initialize(self, create_session):
        self.create_session = create_session

    def require_auth(self, session):
        """Return the authorized user's username.

        If authorization fails, raise HTTPError. This doesn't attempt to
        gracefully handle invalid authentication headers.
        """
        try:
            auth_header = self.request.headers.get("Authorization")
            if auth_header is None:
                raise ValueError("No Authorization header provided")
            auth_type, auth_digest = auth_header.split(" ")
            user, passwd = base64.decodestring(auth_digest).split(":")
            if auth_type != "Basic":
                raise ValueError("Authorization type is not Basic")
            user_model = session.query(models.User).get(user)
            if user_model is None:
                raise ValueError("Invalid username or password")
            passwd_hash = user_model.password_hash
            if pbkdf2.crypt(passwd, passwd_hash) != passwd_hash:
                raise ValueError("Invalid username or password")
        except ValueError as e:
            msg = "Authorization failed: {}".format(e)
            raise tornado.web.HTTPError(401, msg)
        else:
            return user

    def require_body_schema(self, schema):
        """Return json body of the request.

        Raises 400 if the body does not match the given schema.
        """
        try:
            body_json = json.loads(self.request.body)
            jsonschema.validate(body_json, schema)
            return body_json
        except jsonschema.ValidationError as e:
            reason = "Body input validation failed: {}".format(e.message)
            raise tornado.web.HTTPError(400, reason=reason)

    def write_error(self, status_code, **kwargs):
        # if unauthorized, tell client that authorization is required
        if status_code == 401:
            self.set_header('WWW-Authenticate', 'Basic realm=Restricted')

        # use generic error message, or reason if provided
        message = httplib.responses[status_code]
        if "exc_info" in kwargs:
            reason = kwargs["exc_info"][1].reason
            if reason is not None:
                message = reason

        # return errors in JSON
        self.finish({
            "error": {
                "code": status_code,
                "message": message,
            }
        })

    @contextmanager
    def get_db_session(self):
        """Return SQLAlchemy session context manager.

        Commit or rollback is handled authmatically when the context manager
        exits.

        Example:
        with self.get_session() as session:
            session.add(blah)
        """
        session = self.create_session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
