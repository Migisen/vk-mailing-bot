from contextlib import contextmanager

from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

Base = declarative_base()
global_session: Session = None


class ChatIds(Base):
    __tablename__ = 'group_chats'

    chat_id = Column('Id', Integer, primary_key=True)

    def __init__(self, chat_id):
        self.chat_id = chat_id


class PostHistory(Base):
    __tablename__ = 'post_history'

    latest_post = Column('Post_ID', Integer, primary_key=True)

    def __init__(self, latest_post):
        self.latest_post = latest_post


def init_db(engine):
    Base.metadata.create_all(engine)
    global global_session
    global_session = sessionmaker(bind=engine)


@contextmanager
def session_scope() -> Session:
    # noinspection PyCallingNonCallable
    session: Session = global_session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
