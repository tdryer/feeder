from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import (create_engine, Column, ForeignKey, Integer, Table,
                        Sequence, String, UniqueConstraint)
import yaml
import logging

logger = logging.getLogger(__name__)

BASE = declarative_base()

SMALL_STR = 100
MEDIUM_STR = 2048
LARGE_STR = 50 * MEDIUM_STR # ~100k entry content


def initialize_db(database_uri='sqlite://'):
    """Initialize the DB and return SQLAlchemy Session class.

    This should only be called once when the server starts.
    """
    engine = create_engine(database_uri, echo=False)

    # create tables and prepare to make sessions
    BASE.metadata.create_all(engine)
    return sessionmaker(bind=engine)


subscriptions_table = Table('subscriptions', BASE.metadata,
                            Column('username', String(SMALL_STR),
                                   ForeignKey('users.username',
                                              ondelete='CASCADE')),
                            Column('feed_id', Integer,
                                   ForeignKey('feeds.id',
                                              ondelete='CASCADE')))
read_table = Table('read', BASE.metadata,
                   Column('username', String(SMALL_STR),
                          ForeignKey('users.username', ondelete='CASCADE')),
                   Column('entry_id', Integer,
                          ForeignKey('entries.id', ondelete='CASCADE')))


class User(BASE):
    __tablename__ = 'users'

    username = Column(String(SMALL_STR), primary_key=True, nullable=False)
    password_hash = Column(String(MEDIUM_STR), nullable=False)

    subscriptions = relationship('Feed', secondary=subscriptions_table,
                                 backref='users', order_by='Feed.title')
    read_entries = relationship('Entry', secondary=read_table,
                                backref='read_by', lazy='dynamic')

    def __init__(self, name, password_hash):
        self.username = column_size(name, SMALL_STR)
        self.password_hash = column_size(password_hash, MEDIUM_STR)

    def __repr__(self):
        return "<User('%s')>" % (self.username)

    # Subscription related stuff

    def has_subscription(self, feed):
        """Check if the user is subscribed to this feed."""
        return feed in self.subscriptions

    def subscribe(self, feed):
        """Subscribe the user to a feed."""
        self.subscriptions.append(feed)

    def unsubscribe(self, feed):
        """Unsubscribe the user from a feed."""
        self.subscriptions.remove(feed)

    # Entry related stuff

    def has_read(self, entry):
        """Check if the user has marked this entry as read."""
        return bool(self.read_entries.filter(Entry.id == entry.id).count())

    def read(self, entry):
        """Mark the entry as read."""
        self.read_entries.append(entry)

    def unread(self, entry):
        """Mark the entry as unread."""
        self.read_entries.remove(entry)

    def get_entries(self, ids):
        """Retrieve all entries, by their ids, from feeds that the user is
           subscribed to."""
        entries = []
        for feed in self.subscriptions:
            for entry in feed.entries.filter(Entry.id.in_(ids)).all():
                entries.append(entry)
        return entries

    def get_num_unread_entries(self, feed):
        """Count the total number of entries the user has in a feed."""
        total = feed.entries.count()
        read = self.read_entries.filter_by(feed_id=feed.id).count()
        return total - read


class Feed(BASE):
    __tablename__ = 'feeds'

    id = Column(Integer, Sequence('feed_id_seq'), primary_key=True,
                nullable=False)
    title = Column(String(MEDIUM_STR), nullable=False)
    #feed resource
    feed_url = Column(String(MEDIUM_STR), unique=True, nullable=False)
    # url of html page associated with the feed (None if not provided)
    site_url = Column(String(MEDIUM_STR), nullable=True)
    # url of image associated with feed (None if no image)
    image_url = Column(String(MEDIUM_STR), nullable=True)
    # date of last attempted refresh
    last_refresh_date = Column(Integer, nullable=True)
    # last-modifed date used for caching (string since we don't parse it)
    last_modified = Column(String(SMALL_STR), nullable=True)
    # etag used for caching
    etag = Column(String(MEDIUM_STR), nullable=True)

    entries = relationship('Entry', backref='feed', lazy='dynamic',
                           order_by='desc(Entry.date)')

    @staticmethod
    def find_last_updated_before(session, unix_date):
        """Return all feeds with last_modified earlier than unix_date."""
        return session.query(Feed).filter(Feed.last_refresh_date < unix_date)\
                                  .all()

    def __init__(self, title, feed_url, site_url, last_modified=None,
                 etag=None, last_refresh_date=None, image_url=None, id=None):
        self.id = id
        self.title = column_size(title, MEDIUM_STR)
        self.feed_url = column_size(feed_url, MEDIUM_STR)
        self.site_url = column_size(site_url, MEDIUM_STR)
        self.image_url = column_size(image_url, MEDIUM_STR)
        self.last_modified = column_size(last_modified, SMALL_STR)
        self.etag = column_size(etag, MEDIUM_STR)
        self.last_refresh_date = last_refresh_date

    def __repr__(self):
        return "<RSSFeed('%s','%s')>" % (self.title, self.site_url)

    # Entry related stuff

    def add(self, entry):
        """Add an entry to the feed."""
        self.entries.append(entry)

    def add_all(self, entries):
        """Add all entries from an iterable to the feed."""
        for entry in entries:
            self.add(entry)

    def get_entries(self, user, filter_=None):
        """Retrieve all entries for a user from the feed.
           The entries can optionally be filtered by read or unread."""
        for entry in self.entries.all():
            if filter_ == 'read' and not user.has_read(entry):
                continue
            elif filter_ == 'unread' and user.has_read(entry):
                continue
            yield entry


class Entry(BASE):
    __tablename__ = 'entries'
    __table_args__ = (UniqueConstraint('feed_id', 'guid', name='feed_guid'),)

    id = Column(Integer, Sequence('entry_id_seq'), primary_key=True,
                nullable=False)
    feed_id = Column(Integer, ForeignKey('feeds.id', ondelete='CASCADE'),
                     nullable=False)
    content = Column(String(LARGE_STR), nullable=False)
    url = Column(String(MEDIUM_STR), nullable=False)
    title = Column(String(MEDIUM_STR), nullable=False)
    author = Column(String(SMALL_STR), nullable=False)
    date = Column(Integer, nullable=False)
    guid = Column(String(SMALL_STR), nullable=False)

    def __init__(self, content, url, title, author, date, guid):
        self.content = column_size(content, LARGE_STR)
        self.url = column_size(url, MEDIUM_STR)
        self.title = column_size(title, MEDIUM_STR)
        self.author = column_size(author, SMALL_STR)
        self.date = date
        self.guid = column_size(guid, SMALL_STR)

    def __repr__(self):
        return '<Entry({!r})>'.format(self.id)


def column_size(string, size):
    if string is None:
        return string
    if len(string) > size:
        truncated_string = string[:size-6]+" . . ."
        logger.info(
            "Truncated input '{}' to '{}'".format(string, truncated_string)
        )
        return truncated_string
    else:
        return string


def make_yaml_bindings():
    """Use some magic to let yaml dump and load our database models."""

    # XXX: I would like to put this somewhere else but it has to be after all
    #      the classes are created.
    for name, cls in BASE._decl_class_registry.iteritems():
        if name.startswith(u'_sa_'):
            continue

        tag = '!{}'.format(name.lower())

        def representer(dumper, obj, tag=tag):
            cols = dict((item[0], item[1]) for item in obj.__dict__.iteritems()
                        if not item[0].startswith(u'_sa_'))
            return dumper.represent_mapping(tag, cols)

        def constructor(loader, node, cls=cls):
            values = loader.construct_mapping(node)
            return cls(**values)

        yaml.add_representer(cls, representer)
        yaml.SafeDumper.add_representer(cls, representer)
        yaml.add_constructor(tag, constructor)
        yaml.SafeLoader.add_constructor(tag, constructor)


make_yaml_bindings()
