import types
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import make_transient
from sqlalchemy.orm import backref, relationship, sessionmaker
from sqlalchemy import and_, create_engine
from sqlalchemy import Column, ForeignKey, Integer, Sequence, String

Base = declarative_base()
# hard coded might not be the best approach
engine = create_engine('sqlite:///dbtest', echo=False)

class User(Base):
    __tablename__ = 'users'

    username = Column(String, primary_key=True)
    password_hash = Column(String)

    def __init__(self, name, pwhash):
        self.username = name
        self.password_hash = pwhash

    def __repr__(self):
        return "<User('%s')>" % (self.username)

    def save(self, session):
        session.add(self)
        session.commit()

    def remove(self, session):
        session.delete(self)
        # also remove subscriptions for this user
        subs = session.query(Subscription).filter(Subscription.username == self.username).all()
        for sub in subs:
            session.delete(sub)
        session.commit()
        make_transient(self)

    def subscribe(self, session, feed_id):
        sub = Subscription(self.username, feed_id)
        session.add(sub)
        session.commit()

    def unsubscribe(self, session, feed_id):
        sub = session.query(Subscription).filter(and_(Subscription.username == self.username, Subscription.feed_id == feed_id)).one()
        session.delete(sub)
        session.commit()

    def markRead(self, session, entry_id):
        read = Read(self.username, entry_id)
        session.add(read)
        session.commit()

    def getReadIds(self, session):
        id_list = []
        reads = session.query(Read).filter(Read.username == self.username).all()
        for read in reads:
            id_list.append(read.entry_id)
        return id_list

    def getFeeds(self, session):
        id_list = []
        subs = session.query(Subscription).filter(Subscription.username == self.username).all()
        for sub in subs:
            id_list.append(sub.feed_id)
        feeds = session.query(Feed).filter(Feed.id.in_(id_list)).all()
        return feeds

class Feed(Base):
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

    def save(self, session):
        session.add(self)
        session.commit()

    def remove(self, session):
        # check that no users are subscribed
        if session.query(Subscription).filter(Subscription.feed_id == self.id).count() == 0:
            session.delete(self)
            session.commit()
            make_transient(self)

    def getEntries(self, session):
        entries = session.query(Entry).filter(Entry.feed_id == self.id).all()
        return entries

    def getUnreadEntries(self, session, id_list):
        entries = session.query(Entry).filter(and_(Entry.feed_id == self.id, ~Entry.id.in_(id_list))).all()
        return entries

    def getUsers(self, session):
        name_list = []
        subs = session.query(Subscription).filter(Subscription.feed_id == self.id).all()
        for sub in subs:
            name_list.append(sub.username)
        users = session.query(User).filter(User.username.in_(name_list)).all()
        return users

class Entry(Base):
    __tablename__ = 'entries'

    id = Column(Integer, Sequence('entry_id_seq'), primary_key=True)
    feed_id = Column(Integer, ForeignKey('feeds.id'))
    content = Column(String)
    title = Column(String)
    author = Column(String)
    date = Column(Integer)
    guid = Column(String)

    def __init__(self, feed_id, content, title, author, date):
        self.feed_id = feed_id
        self.content = content
        self.title = title
        self.author = author
        self.date = date

    def __repr__(self):
        return "<FeedItem('%s','%s','%s')>" % (self.title, self.author, self.date)

    def save(self, session):
        session.add(self)
        session.commit()

    def remove(self, session):
        session.delete(self)
        session.commit()
        make_transient(self)

class Subscription(Base):
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


class Read(Base):
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
        return "<Read('%s','%s')>" % (self.username, self.entry)

# create tables and prepare to make sessions
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
