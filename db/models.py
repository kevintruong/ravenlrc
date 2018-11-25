from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


def get_db(user, password, host, dbname):
    """Opens a new database connection if there is none yet for the
    current application context.
    """

    # This engine just used to query for list of databases
    dbengine = create_engine('mysql://{0}:{1}@{2}/{3}'.format(user,
                                                              password, host, dbname))
    return dbengine


db_engine = get_db('root', 'hanhdoan', 'localhost', 'youtubecreatordb')
Base = declarative_base(db_engine)


class youtubemv(Base):
    __tablename__ = 'YoutubeMV'
    __table_args__ = {'autoload': True}


class lyric(Base):
    __tablename__ = 'Lyric'
    __table_args__ = {'autoload': True}
    pass


class title(Base):
    __tablename__ = 'Title'
    __table_args__ = {'autoload': True}


class song(Base):
    __tablename__ = 'Song'
    __table_args__ = {'autoload': True}
    pass


class screentemplate(Base):
    __tablename__ = 'ScreenTemplate'
    __table_args__ = {'autoload': True}
    pass


class affect(Base):
    """
    `id` int not null auto_increment,
    `afffectfile` varchar(45) null,
    `opacity` int null,
    """
    __tablename__ = 'Affect'
    __table_args__ = {'autoload': True}
    pass


class screen(Base):
    __tablename__ = 'Screen'
    __table_args__ = {'autoload': True}
    pass


class screenconfiguration(Base):
    __tablename__ = 'ScreenConfiguration'
    __table_args__ = {'autoload': True}
    pass


def loadSession():
    """"""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    return session
