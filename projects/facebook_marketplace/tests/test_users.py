from app.models.user import UserDB
from sqlmodel import select


def test_create_user(client, session):
    response = client.post(
        "/users/",
        json={"username": "tempe", "password": "abc", "email": "tempe@gmail.com"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["username"] == "tempe"
    assert data["email"] == "tempe@gmail.com"

    user = session.exec(select(UserDB).where(UserDB.username == "tempe")).first()
    assert user is not None


def test_duplicate_username(client, session):
    client.post(
        "/users/",
        json={"username": "tempe", "password": "abc", "email": "tempe@gmail.com"},
    )

    response = client.post(
        "/users/",
        json={"username": "tempe", "password": "abc", "email": "other@gmail.com"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Username or email already exists"

    user = session.exec(select(UserDB).where(UserDB.username == "tempe")).first()
    assert user is not None


def test_duplicate_email(client, session):
    client.post(
        "/users/",
        json={"username": "tempe", "password": "abc", "email": "tempe@gmail.com"},
    )

    response = client.post(
        "/users/",
        json={"username": "other", "password": "abc", "email": "tempe@gmail.com"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Username or email already exists"

    user = session.exec(select(UserDB).where(UserDB.username == "other")).first()
    assert user is None
