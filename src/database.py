from sqlalchemy import create_engine, Column, Integer, BigInteger
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///data/bot.db"
engine = create_engine(DATABASE_URL, echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(BigInteger, unique=False, nullable=False)
    chat_id = Column(BigInteger, nullable=False)


Base.metadata.create_all(engine)


def is_duplicate(message_id: int, chat_id: int) -> bool:
    session = SessionLocal()
    exists = session.query(Message).filter_by(
        message_id=message_id, chat_id=chat_id
    ).first() is not None
    session.close()
    return exists


def save_message(message_id: int, chat_id: int):
    session = SessionLocal()
    session.add(Message(message_id=message_id, chat_id=chat_id))
    session.commit()
    session.close()
