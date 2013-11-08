"""AuthProvider abstract class and implementations.

AuthProviders are responsible for keeping track of registered usings,
registering new users, and authenicating usernames and passwords.
"""

from abc import ABCMeta, abstractmethod


class AuthProvider(object):

    """Allow registering and authenticating users."""

    __metaclass__ = ABCMeta

    @abstractmethod
    def _user_exists(self, username):
        """Return True if the given username is already registered."""
        raise NotImplementedError

    @abstractmethod
    def _password_correct(self, username, password):
        """Return True if the given username and password are valid.

        Assume that the username exists.
        """
        raise NotImplementedError

    @abstractmethod
    def _set_credentials(self, username, password):
        """Set the username and password for a new user.

        Assume that the username does not already exist.
        """
        raise NotImplementedError

    def authenticate(self, username, password):
        """Return True if the given username and password are valid."""
        return (self._user_exists(username)
                and self._password_correct(username, password))

    def register(self, username, password):
        """Register a new user.

        Raises ValueError if the username is already taken.
        """
        if self._user_exists(username):
            raise ValueError("Username already registered")
        else:
            self._set_credentials(username, password)
            return True


class DummyAuthProvider(AuthProvider):

    """AuthProvider that just uses an in-memory dictionary for persistence."""

    def __init__(self):
        self._data = {}

    def _user_exists(self, username):
        return username in self._data

    def _password_correct(self, username, password):
        return self._data[username] == password

    def _set_credentials(self, username, password):
        self._data[username] = password
