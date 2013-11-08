from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, ForeignKey, Integer, Sequence, String

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    username = Column(String(50), primary_key=True)
    password_hash = Column(String(255))

    def __init__(self, name, pwhash):
        self.username = name
        self.password_hash = pwhash

    def __repr__(self):
        return "<User('%s')>" % (self.username)

class Feed(Base):
    __tablename__ = 'feeds'

    id = Column(Integer, Sequence('feed_id_seq'), 
primary_key=True)
    title = Column(String(255))
    feed_url = Column(String(255)) # feed resource
    site_url = Column(String(255)) # main site
    last_refresh_date = Column(String(30)) # HTTP format Sun, 06 Nov 1994 08:49:37 GMT
    entries = relationship("Entry", order_by="Entry.date", backref="feed")

    def __init__(self, title, feed_url, site_url):
        self.title = title
        self.feed_url = feed_url
        self.site_url = site_url
        #self.last_refresh_date = now()

    def __repr__(self):
        return "<RSSFeed('%s','%s')>" % (self.title, self.site_url)

class Entry(Base):
    __tablename__ = 'entries'

    id = Column(Integer, Sequence('entry_id_seq'), primary_key=True)
    feed_id = Column(Integer, ForeignKey('feeds.id'))
    content = Column(String(2048))
    title = Column(String(255))
    author = Column(String(50))
    date = Column(String(10)) # format: YYYY-MM-DD
    guid = Column(String(1024))

    def __init__(self, feed_id, content, title, author, date):
        self.feed_id = feed_id
        self.content = content
        self.title = title
        self.author = author
        self.date = date

    def __repr__(self):
        return "<FeedItem('%s','%s','%s')>" % (self.title, self.author, self.date)

class Subscription(Base):
    __tablename__ = 'subscriptions'

    username = Column(String(50), ForeignKey('users.username'), primary_key=True)
    feed_id = Column(Integer, ForeignKey('feeds.id'), primary_key=True)

    def __init__(self, user, feed):
        self.username = user
        self.feed_id = feed

    def __repr__(self):
        return "<Subscription('%s','%s')>" % (self.username, self.feed_id)

class Read(Base):
    __tablename__ = 'reads'

    username = Column(String(50), ForeignKey('users.username'), primary_key=True)
    entry = Column(Integer, ForeignKey('entries.id'), primary_key=True)

    def __init__(self, user, entry_id):
        self.username = user
        self.entry = entry_id

    def __repr__(self):
        return "<Read('%s','%s')>" % (self.username, self.entry)
