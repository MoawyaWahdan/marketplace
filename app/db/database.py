from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    echo=False,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def create_db_and_tables():
    Base.metadata.create_all(bind=engine)


def get_session():
    with SessionLocal() as db:
        yield db
