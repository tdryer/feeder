"""Test implementations of AuthProvider."""

import pytest

from feedreader.auth_provider import DummyAuthProvider


@pytest.fixture(params=[DummyAuthProvider])
def auth_provider(request):
    auth = request.param()
    auth.register("foo", "foopass")
    auth.register("bar", "barpass")
    return auth


def test_sucess(auth_provider):
    assert auth_provider.authenticate("foo", "foopass")
    assert auth_provider.authenticate("bar", "barpass")


def test_wrong_password(auth_provider):
    assert not auth_provider.authenticate("foo", "notfoopass")


def test_wrong_username(auth_provider):
    assert not auth_provider.authenticate("notfoo", "foopass")


def test_register_taken_username(auth_provider):
    assert not auth_provider.register("foo", "otherpass")
    assert auth_provider.authenticate("foo", "foopass")
