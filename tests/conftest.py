import pytest
from sqlmodel import create_engine, Session, SQLModel
from fastapi.testclient import TestClient

from app.main import app
from app.db.database import get_session

test_engine = create_engine(
    "sqlite:///test.db", connect_args={"check_same_thread": False}
)

# Create tables once
SQLModel.metadata.create_all(test_engine)


# REAL override function (NOT pytest fixture)
def override_get_session():
    with Session(test_engine) as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


@pytest.fixture
def session():
    with Session(test_engine) as s:
        yield s


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def clean_db():
    SQLModel.metadata.drop_all(test_engine)
    SQLModel.metadata.create_all(test_engine)
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
