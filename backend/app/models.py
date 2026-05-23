from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, create_engine, Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

class Base(DeclarativeBase):
    pass


class Title(Base):
    __tablename__ = "titles"

    id = Column(Integer, primary_key=True, index=True)
    tmdb_id = Column(String, unique=True, index=True)
    title = Column(String, index=True)
    year = Column(Integer)
    type = Column(String)  # movie or series
    rating = Column(Float, nullable=True)
    popularity_rank = Column(Integer)
    poster_url = Column(String, nullable=True)
    overview = Column(Text, nullable=True)
    trailer_url = Column(String, nullable=True)
    genres = Column(String, nullable=True)  # JSON array as string
    position = Column(Integer)  # position in TOP 10
    scraped_at = Column(DateTime, default=datetime.utcnow)


def get_engine(database_url: str) -> Engine:
    return create_engine(
        database_url,
        connect_args={"check_same_thread": False} if "sqlite" in database_url else {}
    )


def get_session_local(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)
