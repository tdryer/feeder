import types
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, and_
from .models import *

# hard coded might not be the best approach
engine = create_engine('sqlite:///dbtest', echo=False)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

"""
User functions
"""

"""
creates new users or updates users in the database
input: a list of User instances, or a single instance
output: a list of the same User instances, with non-user instances removed
"""


def saveUsers(users):
    if not isinstance(users, types.ListType):
        users = [users]
    user_list = []
    query_filter = []
    session = Session()
    # add all User instances into the session and commit
    for user in users:
        if isinstance(user, User):
            session.add(user)
            query_filter.append(user.username)
    session.commit()
    # query the session for all created/updated users
    user_list = session.query(User).filter(
        User.username.in_(query_filter)).all()
    session.close()

    return user_list

"""
deletes a subset of users from the database
precondition: each User instance has been saved
input: a list of User instances, or a single instance
output: the number of users deleted from the database
"""


def removeUsers(users):
    if not isinstance(users, types.ListType):
        users = [users]
    count = 0
    session = Session()
    for user in users:
        if isinstance(user, User):
            session.delete(user)
            count += 1
    session.commit()
    session.close()

    return count

"""
collects a subset of users from the database
input: a list of usernames to filter for, or an empty list
output: a list of users with names in the input, no users, or all users
"""


def getUsers(names):
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
creates new feeds or updates feeds in the database
input: a list of Feed instances, or a single instance
output: a list of the same Feed instances, with non-instances removed
"""


def saveFeeds(feeds):
    if not isinstance(feeds, types.ListType):
        feeds = [feeds]
    feed_list = []
    query_filter = []
    session = Session()
    # add all Feed instances into the session and commit
    for feed in feeds:
        if isinstance(feed, Feed):
            session.add(feed)
            # this allows us to access the id given to feed when added
            session.flush()
            query_filter.append(feed.id)
    session.commit()
    # query the session for all created/updated feeds
    feed_list = session.query(Feed).filter(Feed.id.in_(query_filter)).all()
    session.close()

    return feed_list

"""
deletes a subset of feeds in the database
precondition: each Feed instance has been saved
input: a list of Feed instances, or a single instance
output: the number of feeds deleted from the database
"""


def removeFeeds(feeds):
    if not isinstance(feeds, types.ListType):
        feeds = [feeds]
    count = 0
    session = Session()
    for feed in feeds:
        if isinstance(feed, Feed):
            # check that no users are subscribed to this feed
            if session.query(Subscription).filter(Subscription.feed_id == feed.id).count() == 0:
                session.delete(feed)
                count += 1
    session.commit()
    session.close()

    return count

"""
collects a subset of feeds from the database
input: a list of filters, or an empty list
output: a list of feeds with attributes in the input, no feeds, or all feeds
"""


def getFeeds(filters):
    session = Session()
    if filters == []:
        feed_list = session.query(Feed).all()
    else:
        # TODO
        pass
    session.close()

    return feed_list


"""
Entry functions
"""

"""
creates new entries or updates entries in the database
input: a list of Entry instances, or a single instance
output: a list of the same Entry instances, with non-user instances removed
"""


def saveEntries(entries):
    if not isinstance(entries, types.ListType):
        entries = [entries]
    entry_list = []
    query_filter = []
    session = Session()
    # add all Entry instances into the session and commit
    for entry in entries:
        if isinstance(entry, Entry):
            session.add(entry)
            # this allows us to access the id given to entry when added
            session.flush()
            query_filter.append(entry.id)
    session.commit()
    # query the session for all created/updated entries
    entry_list = session.query(Entry).filter(Entry.id.in_(query_filter)).all()
    session.close()

    return entry_list

"""
deletes a subset of entries in the database
precondition: each Entry instance has been saved
input: a list of Entry instances, or a single instance
output: the number of entries deleted from the database
"""


def removeEntries(entries):
    if not isinstance(entries, types.ListType):
        entries = [entries]
    count = 0
    session = Session()
    for entry in entries:
        if isinstance(entry, Entry):
            session.delete(entry)
            count += 1
    session.commit()
    session.close()

    return count

"""
collects a subset of entries from the database
input: a feed id
output: a list of entries associated with the feed
"""


def getFeedEntries(feed):
    session = Session()
    entry_list = session.query(Entry).filter(Entry.feed_id == feed).all()
    session.close()

    return entry_list


"""
Subscription functions
"""

"""
associates a user with a feed
precondition: the user and feed have been saved
input: the username and feed id
"""


def subscribe(user, feed):
    subscription = Subscription(user, feed)
    session = Session()
    session.add(subscription)
    session.commit()
    session.close()

"""
disassociates a user with a feed
precondition: the user and feed have been saved
input: the username and feed id
"""


def unsubscribe(user, feed):
    session = Session()
    subscription = session.query(
        Subscription).filter(
        and_(
            User.username == user,
            Feed.id == feed)).first(
    )
    if not subscription is None:
        session.delete(subscription)
    session.commit()
    session.close()

"""
retrieves all records of subscribed feeds for a user
input: the username
output: a list of feed ids the user is subscribed to
"""


def getUserSubs(user):
    id_list = []
    session = Session()
    records = session.query(
        Subscription).filter(
        Subscription.username == user).all(
    )
    session.close()
    for record in records:
        id_list.append(record.feed_id)

    return id_list


"""
Read functions
"""

"""
records that a user has read an entry
precondition: the user and entry have been saved
input: the username and entry id
"""


def markRead(user, entry):
    read = Read(user, entry)
    session = Session()
    session.add(read)
    session.commit()
    session.close()

"""
retrieves all records of read entries for a user
input: the username
output: a list of entry ids the user has read
"""


def getUserRead(username):
    id_list = []
    session = Session()
    records = session.query(Read).filter(Read.username == username).all()
    session.close()
    for record in records:
        id_list.append(record.entry_id)

    return id_list
