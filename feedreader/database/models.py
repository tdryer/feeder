"""SQLAlchemy models."""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import make_transient
from sqlalchemy.orm import sessionmaker
from sqlalchemy import (and_, create_engine, Column, ForeignKey, Integer,
                        Sequence, String)


BASE = declarative_base()


def initialize_db():
    """Initialize the DB and return SQLAlchemy Session class.

    This should only be called once when the server starts.
    """
    # hard coded might not be the best approach
    engine = create_engine('sqlite://', echo=False)

    # create tables and prepare to make sessions
    BASE.metadata.create_all(engine)
    return sessionmaker(bind=engine)

# Counts the number of Feeds with id == feed_id, i.e., returns 0 or 1


def exists_feed(session, feed_id):
    return session.query(Feed).filter(Feed.id == feed_id).count()


class User(BASE):
    __tablename__ = 'users'

    username = Column(String, primary_key=True)
    password_hash = Column(String)

    def __init__(self, name, pwhash):
        self.username = name
        self.password_hash = pwhash

    def __repr__(self):
        return "<User('%s')>" % (self.username)

    def remove(self, session):
        # remove subscriptions for this user
        subs = session.query(
            Subscription).filter(
            Subscription.username == self.username).all()
        for sub in subs:
            session.delete(sub)
        # also remove read entries
        reads = session.query(Read).filter(
            Read.username == self.username
        ).all()
        for read in reads:
            session.delete(read)
        session.delete(self)
        make_transient(self)

    def subscribe(self, session, feed_id):
        sub = Subscription(self.username, feed_id)
        session.add(sub)

    # checks if the user is subscribed to the feed with id == feed_id
    def is_sub_of_feed(self, session, feed_id):
        return session.query(Subscription).filter(and_(
            Subscription.username == self.username,
            Subscription.feed_id == feed_id,
        )).count()

    def unsubscribe(self, session, feed_id):
        sub = session.query(
            Subscription).filter(
            and_(
                Subscription.username == self.username,
                Subscription.feed_id == feed_id)).one(
        )
        session.delete(sub)

    # checks if the user is allowed to view the entry with id == entry_id
    def can_read(self, session, entry_id):
        entry = session.query(Entry).filter(Entry.id == entry_id).one()
        return self.is_sub_of_feed(session, entry.feed_id)

    def mark_read(self, session, entry_id):
        read = Read(self.username, entry_id)
        session.add(read)

    # checks if the user has read the entry with id == entry_id
    def has_read(self, session, entry_id):
        return session.query(Read).filter(and_(
                Read.username == self.username,
                Read.entry_id == entry_id
                )).count()

    def num_unread_in_feed(self, session, feed_id):
        read_ids = self.get_read_ids(session)
        if read_ids != []:
            return session.query(Entry).filter(and_(
                Entry.feed_id == feed_id,
                ~Entry.id.in_(read_ids)
            )).count()
        else:
            return session.query(Entry).filter(Entry.feed_id == feed_id
                                               ).count()

    def get_read_ids(self, session):
        id_list = []
        reads = session.query(
            Read).filter(
            Read.username == self.username).all(
        )
        for read in reads:
            id_list.append(read.entry_id)
        return id_list

    def get_feeds(self, session):
        id_list = []
        subs = session.query(
            Subscription).filter(
            Subscription.username == self.username).all(
        )
        for sub in subs:
            id_list.append(sub.feed_id)
        feeds = session.query(Feed).filter(Feed.id.in_(id_list)).all()
        return feeds

    """
    Collects all the entries of a feed
    precondition: is_sub_of_feed should be called prior to
                  this function call
    Input: session, Feed.id, optional: filter="read"|"unread"
    Ouput: a list of entries
    """

    def get_feed_entries(self, session, feed_id, **kwargs):
        do_filter = False
        if 'filter' in kwargs:
            entry_filter = kwargs.get('filter')
            do_filter = True
        # Queries
        entry_ids = []
        # Can't make this a single statement because query(Entry.id) produces
        #  a list [(1,), (2,), . . . ]
        for row in session.query(Entry).filter(
                Entry.feed_id == feed_id).all():
            entry_ids.append(row.id)
        read_ids = []
        if entry_ids != []:
            for row in session.query(Read).filter(and_(
                    Read.username == self.username,
                    Read.entry_id.in_(entry_ids)
            )).all():
                read_ids.append(row.entry_id)
        raw_entries = session.query(Entry).filter(Entry.feed_id == feed_id)\
                                          .order_by(Entry.date.desc()).all()
        if not do_filter:
            return raw_entries
        else:
            feed_entries = []
            if entry_filter == "read":
                for entry in raw_entries:
                    if entry.id in read_ids:
                        feed_entries.append(entry)
            elif entry_filter == "unread":
                for entry in raw_entries:
                    if entry.id not in read_ids:
                        feed_entries.append(entry)

            return feed_entries


class Feed(BASE):
    __tablename__ = 'feeds'

    id = Column(Integer, Sequence('feed_id_seq'),
                primary_key=True)
    title = Column(String)
    feed_url = Column(String)  # feed resource
    site_url = Column(String)  # main site
    last_refresh_date = Column(Integer)

    def __init__(self, title, feed_url, site_url):
        self.title = title
        self.feed_url = feed_url
        self.site_url = site_url
        #self.last_refresh_date = now()

    def __repr__(self):
        return "<RSSFeed('%s','%s')>" % (self.title, self.site_url)

    def remove(self, session):
        # check that no users are subscribed
        if session.query(Subscription).filter(
                Subscription.feed_id == self.id).count() == 0:
            # remove all associated entries
            entries = session.query(Entry).filter(
                Entry.feed_id == self.id
            ).all()
            entry_ids = []
            for entry in entries:
                entry_ids.append(entry.id)
                session.delete(entry)
            reads = session.query(Read).filter(Read.entry_id.in_(entry_ids))\
                                       .all()

            for read in reads:
                session.delete(read)

            session.delete(self)
            make_transient(self)

    def get_entries(self, session):
        return session.query(Entry).filter(Entry.feed_id == self.id).all()

    def get_users(self, session):
        name_list = []
        subs = session.query(
            Subscription).filter(
            Subscription.feed_id == self.id).all(
        )
        for sub in subs:
            name_list.append(sub.username)
        users = session.query(User).filter(User.username.in_(name_list)).all()
        return users


class Entry(BASE):
    __tablename__ = 'entries'

    id = Column(Integer, Sequence('entry_id_seq'), primary_key=True)
    feed_id = Column(Integer, ForeignKey('feeds.id'))
    content = Column(String)
    url = Column(String)
    title = Column(String)
    author = Column(String)
    date = Column(Integer)
    guid = Column(String)

    def __init__(self, feed_id, content, url, title, author, date):
        self.feed_id = feed_id
        self.content = content
        self.url = url
        self.title = title
        self.author = author
        self.date = date

    def __repr__(self):
        return (
            "<Entry('%s','%s','%s')>" % (
                self.title, self.author, self.date)
        )

    def remove(self, session):
        session.delete(self)
        make_transient(self)

    def been_read(self, session, username):
        if session.query(Read).filter(and_(
                Read.username == username,
                Read.entry_id == self.id
                )).count():
            return "read"
        else:
            return "unread"


class Subscription(BASE):
    __tablename__ = 'subscriptions'

    username = Column(
        String(50),
        ForeignKey('users.username'),
        primary_key=True)
    feed_id = Column(Integer, ForeignKey('feeds.id'), primary_key=True)

    def __init__(self, user, feed):
        self.username = user
        self.feed_id = feed

    def __repr__(self):
        return "<Subscription('%s','%s')>" % (self.username, self.feed_id)


class Read(BASE):
    __tablename__ = 'reads'

    username = Column(
        String(50),
        ForeignKey('users.username'),
        primary_key=True)
    entry_id = Column(Integer, ForeignKey('entries.id'), primary_key=True)

    def __init__(self, user, entry_id):
        self.username = user
        self.entry_id = entry_id

    def __repr__(self):
        return "<Read('%s','%s')>" % (self.username, self.entry_id)
