import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import get_session, Base
import logging

logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)

DATABASE_TEST_URL = os.getenv("DATABASE_TEST_URL")
if not DATABASE_TEST_URL:
    raise ValueError("DATABASE_TEST_URL is not set in environment variables")

engine = create_engine(DATABASE_TEST_URL, echo=False)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


Base.metadata.create_all(bind=engine)


def override_get_session():
    with SessionLocal() as db:
        yield db


app.dependency_overrides[get_session] = override_get_session


@pytest.fixture
def session():
    with SessionLocal() as db:
        yield db


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def user(client):
    response = client.post(
        "/users/",
        json={
            "username": "tempe",
            "password": "abc",
            "email": "tempe@gmail.com",
        },
    )
    assert response.status_code == 200
    return {"username": "tempe", "password": "abc", "email": "tempe@gmail.com"}
