import types
from sqlalchemy import and_
from models import *

"""
User functions
"""

"""
collects a subset of users from the database
input: a list of usernames to filter for, or an empty list
output: a list of users with names in the input, no users, or all users
"""
def fetchUsers(names):
    session = Session()
    if names == []:
        user_list = session.query(User).all()
    else:
        user_list = session.query(User).filter(User.username.in_(names)).all()
    session.close()

    return user_list


"""
Feed functions
"""

"""
collects a subset of feeds from the database
input: a list of filters, or an empty list
output: a list of feeds with attributes in the input, no feeds, or all feeds
"""


def fetchFeeds(*args, **kwargs):
    session = Session()
    if filters == []:
        feed_list = session.query(Feed).all()
    else:
        # TODO
        pass
    session.close()

    return feed_list
